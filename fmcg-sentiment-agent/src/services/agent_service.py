"""
agent_service.py

Owns the one AgentRuntime instance per (framework, model) pair, reused across
requests so the MCP session isn't reopened on every call.
"""

from src.agents.audit import new_session_id
from src.agents.final_config import FRAMEWORK, MODEL
from src.agents.runtime import AgentRuntime

_runtimes = {}

def get_runtime(model=None):
    model = model or MODEL
    key = (FRAMEWORK, model)
    if key not in _runtimes:
        _runtimes[key] = AgentRuntime(FRAMEWORK, model)
    return _runtimes[key]


def ask_assistant(question, role, session_id=None, model=None):
    session_id = session_id or new_session_id()
    runtime = get_runtime(model)
    record = runtime.ask(question, role, session_id)
    return {
        "session_id": session_id,
        "role": role,
        "status": record["status"],
        "answer": record["answer"],
        "interaction_id": record.get("interaction_id"),
        "checks": record.get("checks", {}),
    }

def get_status(model=None):
    model = model or MODEL
    key = (FRAMEWORK, model)
    runtime = _runtimes.get(key)
    if runtime is None:
        return {"started": False, "ready": False, "error": None}
    return {
        "started": True,
        "ready": runtime.ready.is_set(),
        "error": str(runtime.startup_error) if runtime.startup_error else None,
    }
