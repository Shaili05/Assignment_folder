import asyncio
import json
import sys
from datetime import date
from types import SimpleNamespace

from src.mcp import server
from src.mcp.registry import list_specs


class StopServer(Exception):
    pass


def test_tool_definitions_list_every_registered_tool():
    definitions = server.tool_definitions()
    specs = list_specs()
    assert [tool.name for tool in definitions] == [spec["name"] for spec in specs]
    assert all(tool.description for tool in definitions)
    assert all(tool.inputSchema["type"] == "object" for tool in definitions)


def test_list_tools_handler_returns_the_definitions():
    tools = asyncio.run(server.handle_list_tools())
    assert [tool.name for tool in tools] == [spec["name"] for spec in list_specs()]


def test_to_text_content_turns_a_result_into_json_text():
    content = server.to_text_content({"count": 2, "day": date(2023, 3, 21)})
    assert len(content) == 1
    assert content[0].type == "text"
    assert json.loads(content[0].text) == {"count": 2, "day": "2023-03-21"}


def test_call_tool_handler_runs_the_tool_and_returns_text(monkeypatch):
    seen = {}

    def fake_call_tool(name, arguments):
        seen["call"] = (name, arguments)
        return {"ok": True}

    monkeypatch.setattr(server, "call_tool", fake_call_tool)
    content = asyncio.run(server.handle_call_tool("sentiment_trend", {"periods": 3}))
    assert seen["call"] == ("sentiment_trend", {"periods": 3})
    assert json.loads(content[0].text) == {"ok": True}


def test_decorator_turns_input_validation_off_when_supported(monkeypatch):
    class NewServer:
        def call_tool(self, validate_input=True):
            return ("decorator", validate_input)

    monkeypatch.setattr(server, "server", NewServer())
    assert server.call_tool_decorator() == ("decorator", False)


def test_decorator_works_when_validation_cannot_be_turned_off(monkeypatch):
    class OldServer:
        def call_tool(self):
            return "decorator"

    monkeypatch.setattr(server, "server", OldServer())
    assert server.call_tool_decorator() == "decorator"


def test_prepare_server_logs_to_stderr_and_loads_the_models(monkeypatch):
    steps = []
    monkeypatch.setattr(server, "configure_logging", lambda stream: steps.append(("logging", stream)))
    monkeypatch.setattr(server, "warm_up", lambda: steps.append(("warm_up", None)))
    server.prepare_server()
    assert steps == [("logging", sys.stderr), ("warm_up", None)]


def test_main_runs_the_server_on_the_stdio_streams(monkeypatch):
    seen = {}

    class FakeStdio:
        async def __aenter__(self):
            return ("read", "write")

        async def __aexit__(self, *exc_info):
            return False

    async def fake_run(read, write, options):
        seen["run"] = (read, write, options)

    monkeypatch.setattr(server.mcp.server.stdio, "stdio_server", lambda: FakeStdio())
    monkeypatch.setattr(server.server, "run", fake_run)
    monkeypatch.setattr(server.server, "create_initialization_options", lambda: "options")
    asyncio.run(server.main())
    assert seen["run"] == ("read", "write", "options")


