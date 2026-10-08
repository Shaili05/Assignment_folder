import pytest

from src.config.constants import AVAILABLE_MODELS, DEFAULT_MODEL
from src.exceptions.exceptions import InvalidRequestError
from src.services import agent_service


class FakeAgent:
    created = []

    def __init__(self, model):
        self.model = model
        FakeAgent.created.append(model)


@pytest.fixture
def runtimes(monkeypatch):
    FakeAgent.created = []
    monkeypatch.setattr(agent_service, "_agents", {})
    monkeypatch.setattr(agent_service, "ReviewAgent", FakeAgent)
    return agent_service._agents


def test_get_runtime_creates_one_agent_per_model(runtimes):
    first = agent_service.get_runtime(AVAILABLE_MODELS[0])
    assert agent_service.get_runtime(AVAILABLE_MODELS[0]) is first
    second = agent_service.get_runtime(AVAILABLE_MODELS[1])
    assert second is not first
    assert FakeAgent.created == [AVAILABLE_MODELS[0], AVAILABLE_MODELS[1]]


def test_get_runtime_uses_the_default_model(runtimes):
    assert agent_service.get_runtime().model == DEFAULT_MODEL


def test_get_runtime_rejects_an_unknown_model(runtimes):
    with pytest.raises(InvalidRequestError):
        agent_service.get_runtime("made-up:model")
    assert FakeAgent.created == []


def test_get_progress_wraps_the_stages(monkeypatch):
    monkeypatch.setattr(agent_service, "read_progress", lambda session_id: [{"stage": "completed"}])
    assert agent_service.get_progress("s1") == {"stages": [{"stage": "completed"}]}


def test_get_status_reports_a_startup_error(monkeypatch):
    class Ready:
        def is_set(self):
            return False

    broken = type("Broken", (), {"ready": Ready(), "startup_error": RuntimeError("no key")})()
    monkeypatch.setattr(agent_service, "_agents", {DEFAULT_MODEL: broken})
    assert agent_service.get_status() == {"started": True, "ready": False, "error": "no key"}


