"""
backend_autogen.py

Agent backend built with AutoGen AgentChat (AssistantAgent). Tools come from
the MCP server over one persistent session shared by every agent. Each
session/role pair gets its own AssistantAgent, which keeps the conversation
history for follow-up questions.
"""

import contextlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.llm_client import resolve
from agent.prompts import build_system_prompt
from agent.roles import allowed_tools

SERVER_PATH = Path(__file__).resolve().parents[1] / "mcp_server" / "server.py"
MCP_READ_TIMEOUT = 120
MAX_TOOL_ROUNDS = 4


def parse_arguments(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}


def unwrap_tool_output(content):
    # The MCP adapter returns a JSON list of content blocks, the tool result is inside the text field.
    try:
        items = json.loads(content)
    except (TypeError, json.JSONDecodeError):
        return content
    if isinstance(items, list) and items and all(isinstance(i, dict) and "text" in i for i in items):
        return "".join(i.get("text") or "" for i in items)
    return content


def parse_result(messages):
    calls, results, order = {}, {}, []
    prompt_tokens = completion_tokens = 0
    answer = ""

    for message in messages:
        usage = getattr(message, "models_usage", None)
        if usage:
            prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
            completion_tokens += getattr(usage, "completion_tokens", 0) or 0

        kind = getattr(message, "type", "")
        if kind == "ToolCallRequestEvent":
            for call in message.content:
                order.append(call.id)
                calls[call.id] = {"name": call.name, "arguments": parse_arguments(call.arguments)}
        elif kind == "ToolCallExecutionEvent":
            for result in message.content:
                results[result.call_id] = (unwrap_tool_output(result.content), not result.is_error)
        elif kind in ("TextMessage", "ToolCallSummaryMessage") and getattr(message, "source", "") != "user":
            answer = message.content if isinstance(message.content, str) else str(message.content)

    tool_calls = []
    for call_id in order:
        output_text, ok = results.get(call_id, ("", False))
        tool_calls.append({**calls[call_id], "output_text": output_text, "ok": ok})
    return {"answer": answer.strip(), "tool_calls": tool_calls,
            "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}


class AutoGenBackend:
    name = "autogen"

    def __init__(self, model_spec):
        self.model_spec = model_spec
        self.stack = None
        self.tools = []
        self.model_client = None
        self.agents = {}

    async def open(self):
        from autogen_core.models import ModelFamily
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from autogen_ext.tools.mcp import StdioServerParams, create_mcp_server_session, mcp_server_tools

        config = resolve(self.model_spec)
        options = {
            "model": config["model"], "base_url": config["base_url"], "api_key": config["api_key"],
            "model_info": {"vision": False, "function_calling": True, "json_output": False,
                           "family": ModelFamily.UNKNOWN, "structured_output": False},
        }
        if config["provider"] != "gemini":
            options["temperature"] = 0.2
        self.model_client = OpenAIChatCompletionClient(**options)

        params = StdioServerParams(
            command=sys.executable, args=[str(SERVER_PATH)], env=dict(os.environ),
            read_timeout_seconds=MCP_READ_TIMEOUT,
        )
        self.stack = contextlib.AsyncExitStack()
        session = await self.stack.enter_async_context(create_mcp_server_session(params))
        await session.initialize()
        self.tools = await mcp_server_tools(params, session=session)

    async def close(self):
        if self.stack is not None:
            await self.stack.aclose()
        if self.model_client is not None:
            await self.model_client.close()

    def get_agent(self, session_id, role):
        key = (session_id, role)
        if key not in self.agents:
            from autogen_agentchat.agents import AssistantAgent

            permitted = set(allowed_tools(role))
            tools = [t for t in self.tools if t.name in permitted]
            self.agents[key] = AssistantAgent(
                "review_agent",
                model_client=self.model_client,
                tools=tools,
                system_message=build_system_prompt(role),
                reflect_on_tool_use=True,
                max_tool_iterations=MAX_TOOL_ROUNDS,
            )
        return self.agents[key]

    async def ask(self, question, role, session_id):
        agent = self.get_agent(session_id, role)
        result = await agent.run(task=question)
        parsed = parse_result(result.messages)
        if not parsed["answer"]:
            parsed["answer"] = "I could not produce an answer. Please rephrase the question."
        return parsed


