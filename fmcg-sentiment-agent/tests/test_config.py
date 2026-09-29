import pytest

from src.exceptions.exceptions import ConfigurationError
from src.config.settings import resolve_model


def test_resolve_model_rejects_unknown_provider():
    with pytest.raises(ConfigurationError):
        resolve_model("unknown:some-model")


def test_resolve_model_rejects_missing_model_id():
    with pytest.raises(ConfigurationError):
        resolve_model("groq:")


def test_resolve_model_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        resolve_model("groq:openai/gpt-oss-120b")


def test_resolve_model_returns_provider_details(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    config = resolve_model("groq:openai/gpt-oss-120b")
    assert config["provider"] == "groq"
    assert config["model"] == "openai/gpt-oss-120b"
    assert config["base_url"].startswith("https://")


