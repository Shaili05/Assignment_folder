from types import SimpleNamespace

from src.services import agent_service


class FakeAgent:
    def __init__(self, ready=True, startup_error=None):
        self.closed = False
        self.ready = SimpleNamespace(is_set=lambda: ready)
        self.startup_error = startup_error

    def ask(self, question, role, session_id):
        return {
            "status": "answered", "answer": "ok", "interaction_id": "i1", "checks": {},
            "error_detail": "internal only", "tool_calls": [],
        }

    def close(self):
        self.closed = True


def test_ask_assistant_returns_only_public_fields(monkeypatch):
    monkeypatch.setattr(agent_service, "get_runtime", lambda model=None: FakeAgent())
    result = agent_service.ask_assistant("How is packaging?", "brand_manager", "s1")
    assert set(result) == {"session_id", "role", "status", "answer", "interaction_id", "checks"}
    assert result["session_id"] == "s1"


def test_get_status_before_and_after_start(monkeypatch):
    monkeypatch.setattr(agent_service, "_agents", {})
    assert agent_service.get_status("m") == {"started": False, "ready": False, "error": None}
    agent_service._agents["m"] = FakeAgent()
    assert agent_service.get_status("m") == {"started": True, "ready": True, "error": None}


def test_close_runtimes_closes_every_agent(monkeypatch):
    agent = FakeAgent()
    monkeypatch.setattr(agent_service, "_agents", {"m": agent})
    agent_service.close_runtimes()
    assert agent.closed is True
    assert agent_service._agents == {}


