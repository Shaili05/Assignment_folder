import json

import pytest

from src.agents.review_agent import to_app_error
from src.exceptions.exceptions import InvalidRequestError, RateLimitError
from src.services import agent_service
from src.utils.audit_logger import load_log


class ProviderError(Exception):
    def __init__(self, status_code):
        super().__init__(f"provider error {status_code}")
        self.status_code = status_code


def test_a_token_limit_error_is_shown_as_a_rate_limit():
    assert to_app_error(ProviderError(413)).message == RateLimitError.default_message


def test_unknown_model_is_rejected_before_an_agent_is_created(monkeypatch):
    monkeypatch.setattr(agent_service, "_agents", {})
    with pytest.raises(InvalidRequestError):
        agent_service.get_runtime("not-a-model")
    assert agent_service._agents == {}


def test_damaged_audit_lines_are_skipped(tmp_path):
    path = tmp_path / "audit.jsonl"
    lines = [json.dumps({"question": "a"}), "{broken", "", json.dumps({"question": "b"})]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert [record["question"] for record in load_log(path)] == ["a", "b"]
