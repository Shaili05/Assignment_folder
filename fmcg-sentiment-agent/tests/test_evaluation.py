import pandas as pd
import pytest

from src.evaluation.eval_questions import matches, number_variants
from src.evaluation.run_evaluation import ROW_FIELDS, failed_row, score_question, summarize

CLEAN_CHECKS = {
    "cited_review_ids": [], "invalid_citations": [], "unsupported_quotes": [], "unsupported_numbers": [],
}


def make_record(**extra):
    record = {
        "status": "answered", "answer": "Net sentiment was 77.1",
        "tool_calls": [{"name": "sentiment_trend"}], "checks": dict(CLEAN_CHECKS),
        "latency_sec": 1.0, "prompt_tokens": 10, "completion_tokens": 5, "cost_usd": 0.001,
    }
    record.update(extra)
    return record


def test_numbers_match_only_as_whole_numbers():
    assert matches("net sentiment 77.1 overall", "77.1") is True
    assert matches("net sentiment 177.1 overall", "77.1") is False
    assert matches("Packaging is up", "packaging") is True


def test_number_variants():
    assert number_variants(77.1) == ["77", "77.1"]
    assert number_variants(80.0) == ["80", "80.0"]
    assert number_variants(0) == []


def test_a_good_answer_passes():
    question = {"id": "q", "tools": ["sentiment_trend"], "facts": [["77.1"]]}
    row = score_question(question, make_record())
    assert row["passed"] is True
    assert row["tools_called"] == "sentiment_trend"


def test_a_forbidden_tool_fails_the_question():
    question = {"id": "q", "forbidden_tools": ["sentiment_trend"]}
    row = score_question(question, make_record())
    assert row["tool_ok"] is False
    assert row["passed"] is False


def test_an_invalid_citation_fails_grounding():
    checks = {**CLEAN_CHECKS, "invalid_citations": [9]}
    row = score_question({"id": "q"}, make_record(checks=checks))
    assert row["grounded_ok"] is False
    assert row["invalid_citations"] == "9"


def test_error_records_show_the_technical_detail():
    record = make_record(status="error", answer="The assistant hit an error.",
                         error_detail="RateLimitError: slow down", tool_calls=[])
    row = score_question({"id": "q"}, record)
    assert row["passed"] is False
    assert row["answer"].startswith("RateLimitError")


def test_failed_row_has_every_field():
    row = failed_row("could not start")
    assert list(row) == ROW_FIELDS
    assert row["passed"] is False


def test_summarize_pass_rate_and_averages():
    base = {
        "framework": "langgraph", "model": "m", "status": "answered", "status_ok": True,
        "tool_ok": True, "facts_ok": True, "grounded_ok": True,
    }
    frame = pd.DataFrame([
        {**base, "passed": True, "latency_sec": 2.0, "prompt_tokens": 100, "tool_call_count": 1, "cost_usd": 0.001},
        {**base, "passed": False, "latency_sec": 4.0, "prompt_tokens": 300, "tool_call_count": 3, "cost_usd": 0.002},
    ])
    row = summarize(frame).iloc[0]
    assert row["questions"] == 2
    assert row["pass_rate_pct"] == 50.0
    assert row["avg_latency_s"] == 3.0
    assert row["avg_prompt_tokens"] == 200
    assert row["total_cost_usd"] == pytest.approx(0.003)


