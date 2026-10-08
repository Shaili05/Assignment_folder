import logging

from src.agents.review_agent import ReviewAgent
from src.config.constants import AVAILABLE_MODELS, DEFAULT_MODEL
from src.exceptions.exceptions import InvalidRequestError
from src.utils.audit_logger import new_session_id
from src.utils.progress_log import read_progress

logger = logging.getLogger(__name__)

_agents = {}


def get_runtime(model=None):
    model = model or DEFAULT_MODEL
    if model not in AVAILABLE_MODELS:
        raise InvalidRequestError(f"Unknown model '{model}'. Choose one of: {', '.join(AVAILABLE_MODELS)}")
    if model not in _agents:
        logger.info("Creating the assistant for %s", model)
        _agents[model] = ReviewAgent(model)
    return _agents[model]


def ask_assistant(question, role, session_id=None, model=None):
    session_id = session_id or new_session_id()
    record = get_runtime(model).ask(question, role, session_id)
    return {
        "session_id": session_id,
        "role": role,
        "status": record["status"],
        "answer": record["answer"],
        "interaction_id": record.get("interaction_id"),
        "checks": record.get("checks", {}),
    }


def get_status(model=None):
    agent = _agents.get(model or DEFAULT_MODEL)
    if agent is None:
        return {"started": False, "ready": False, "error": None}
    return {
        "started": True,
        "ready": agent.ready.is_set(),
        "error": str(agent.startup_error) if agent.startup_error else None,
    }


def close_runtimes():
    for agent in list(_agents.values()):
        agent.close()
    _agents.clear()


def get_progress(session_id):
    return {"stages": read_progress(session_id)}
