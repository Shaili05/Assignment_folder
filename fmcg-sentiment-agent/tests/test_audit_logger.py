import json

from src.config import constants
from src.utils import audit_logger
from src.utils.audit_logger import (
    REDACTED_FIELDS, estimate_cost, load_log, log_interaction, read_log, usage_summary,
)
from src.utils.output import write_line


def make_record(session_id="s1", question="How is packaging doing?", **extra):
    record = {
        "session_id": session_id, "role": "brand_manager", "question": question,
        "status": "answered", "answer": "Packaging is positive.",
        "model": "groq:openai/gpt-oss-120b", "framework": "langgraph",
        "prompt_tokens": 1000, "completion_tokens": 100, "latency_sec": 2.0,
    }
    record.update(extra)
    return record


def test_log_interaction_writes_one_json_line(tmp_path):
    path = tmp_path / "audit.jsonl"
    entry = log_interaction(make_record(), path)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    saved = json.loads(lines[0])
    assert saved["interaction_id"] == entry["interaction_id"]
    assert "timestamp" in saved


def test_log_interaction_adds_cost_for_a_known_model(tmp_path):
    entry = log_interaction(make_record(), tmp_path / "audit.jsonl")
    assert entry["cost_usd"] == 0.00021


def test_estimate_cost_known_unknown_and_free_models():
    assert estimate_cost("groq:openai/gpt-oss-120b", 1000, 100) == 0.00021
    assert estimate_cost("unknown:model", 1000, 100) is None
    assert estimate_cost("openrouter:some/model:free", 1000, 100) == 0.0


def test_brand_manager_reads_the_full_log(tmp_path):
    path = tmp_path / "audit.jsonl"
    log_interaction(make_record("s1"), path)
    log_interaction(make_record("s2"), path)
    assert len(read_log("brand_manager", path=path)) == 2


def test_support_team_sees_only_its_own_redacted_session(tmp_path):
    path = tmp_path / "audit.jsonl"
    log_interaction(make_record("s1", role="support_team"), path)
    log_interaction(make_record("s2"), path)
    records = read_log("support_team", session_id="s1", path=path)
    assert len(records) == 1
    assert set(records[0]) == set(REDACTED_FIELDS)
    assert "answer" not in records[0]


def test_support_team_without_a_session_sees_nothing(tmp_path):
    path = tmp_path / "audit.jsonl"
    log_interaction(make_record("s1"), path)
    assert read_log("support_team", path=path) == []


def test_load_log_of_a_missing_file_is_empty(tmp_path):
    assert load_log(tmp_path / "missing.jsonl") == []


def test_usage_summary_groups_by_model():
    records = [
        make_record(latency_sec=2.0, cost_usd=0.001),
        make_record(latency_sec=4.0, cost_usd=0.002),
    ]
    summary = usage_summary(records)
    assert len(summary) == 1
    assert summary.iloc[0]["requests"] == 2
    assert summary.iloc[0]["avg_latency_s"] == 3.0
    assert summary.iloc[0]["prompt_tokens"] == 2000


def test_usage_summary_of_no_records_is_empty():
    assert usage_summary([]).empty


def test_write_failure_does_not_raise(tmp_path):
    # A folder path cannot be opened as a file, so the write fails.
    entry = log_interaction(make_record(), tmp_path)
    assert "interaction_id" in entry


def test_prices_come_from_constants():
    assert audit_logger.PRICES is constants.PRICES


def test_write_line_goes_to_stdout(capsys):
    write_line("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
    assert captured.err == ""


