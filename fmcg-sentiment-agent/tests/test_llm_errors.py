import pytest
import sys
from src.config.constants import LLM_MAX_RETRIES
from src.exceptions.exceptions import ConfigurationError, LLMProviderError, RateLimitError
from src.rag import generator
from types import SimpleNamespace

class FakeApiError(Exception):
    def __init__(self, status_code):
        super().__init__(f"api error {status_code}")
        self.status_code = status_code


class FakeClient:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0
        self.chat = self
        self.completions = self

    def create(self, **kwargs):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr(generator.time, "sleep", lambda seconds: None)


def use_client(monkeypatch, outcomes):
    client = FakeClient(outcomes)
    monkeypatch.setattr(generator, "get_client", lambda: client)
    return client


def test_missing_api_key_raises_configuration_error(monkeypatch):
    monkeypatch.setattr(generator, "_state", {})
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        generator.get_client()


def test_rate_limit_retries_then_raises_rate_limit_error(monkeypatch, no_sleep):
    client = use_client(monkeypatch, [FakeApiError(429)] * LLM_MAX_RETRIES)
    with pytest.raises(RateLimitError):
        generator.call_llm([], "any-model")
    assert client.calls == LLM_MAX_RETRIES


def test_rejected_key_fails_at_once_without_retry(monkeypatch, no_sleep):
    client = use_client(monkeypatch, [FakeApiError(401)] * LLM_MAX_RETRIES)
    with pytest.raises(LLMProviderError):
        generator.call_llm([], "any-model")
    assert client.calls == 1


def test_server_errors_end_as_provider_error(monkeypatch, no_sleep):
    client = use_client(monkeypatch, [FakeApiError(500)] * LLM_MAX_RETRIES)
    with pytest.raises(LLMProviderError):
        generator.call_llm([], "any-model")
    assert client.calls == LLM_MAX_RETRIES


def test_call_recovers_after_one_failure(monkeypatch, no_sleep):
    client = use_client(monkeypatch, [FakeApiError(429), "ok"])
    assert generator.call_llm([], "any-model") == "ok"
    assert client.calls == 2


def test_client_is_created_once_with_the_api_key(monkeypatch):
    created = []

    class FakeGroq:
        def __init__(self, api_key):
            created.append(api_key)

    monkeypatch.setitem(sys.modules, "groq", SimpleNamespace(Groq=FakeGroq))
    monkeypatch.setattr(generator, "_state", {})
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    first = generator.get_client()
    assert generator.get_client() is first
    assert created == ["test-key"]


