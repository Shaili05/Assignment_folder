import pandas as pd
import pytest

from src.config.constants import DEFAULT_MODEL, EVAL_ROW_FIELDS
from src.evaluation import eval_questions, run_evaluation
from src.evaluation.eval_questions import matches, number_variants
from src.evaluation.run_evaluation import failed_row, score_question, summarize
from src.exceptions.exceptions import AssistantUnavailableError

CLEAN_CHECKS = {
    "cited_review_ids": [], "invalid_citations": [], "unsupported_quotes": [], "unsupported_numbers": [],
}
QUESTIONS = [
    {"id": "q1", "session": "a", "question": "First question?"},
    {"id": "q2", "session": "a", "question": "Second question?", "role": "support_team"},
    {"id": "q3", "session": "b", "question": "Third question?"},
]


def make_record(**extra):
    record = {
        "status": "answered", "answer": "Net sentiment was 77.1",
        "tool_calls": [{"name": "sentiment_trend"}], "checks": dict(CLEAN_CHECKS),
        "latency_sec": 1.0, "prompt_tokens": 10, "completion_tokens": 5, "cost_usd": 0.001,
    }
    record.update(extra)
    return record


class FakeAgent:
    name = "langgraph"
    instances = []
    start_error = None
    fail_question = None

    def __init__(self, model, audit_path=None):
        self.model = model
        self.asked = []
        self.closed = False
        FakeAgent.instances.append(self)

    def wait_until_ready(self):
        if FakeAgent.start_error:
            raise FakeAgent.start_error

    def ask(self, question, role, session_id):
        self.asked.append((question, role, session_id))
        if question == FakeAgent.fail_question:
            raise RuntimeError("boom")
        return make_record()

    def close(self):
        self.closed = True


@pytest.fixture
def fake_agent(monkeypatch):
    FakeAgent.instances = []
    FakeAgent.start_error = None
    FakeAgent.fail_question = None
    monkeypatch.setattr(run_evaluation, "ReviewAgent", FakeAgent)
    return FakeAgent


@pytest.fixture
def eval_paths(monkeypatch, tmp_path):
    folder = tmp_path / "evaluation"
    monkeypatch.setattr(run_evaluation, "EVALUATION_DIR", folder)
    monkeypatch.setattr(run_evaluation, "EVAL_RESULTS_PATH", folder / "results.csv")
    monkeypatch.setattr(run_evaluation, "EVAL_SUMMARY_PATH", folder / "summary.csv")
    monkeypatch.setattr(run_evaluation, "build_questions", lambda: [dict(q) for q in QUESTIONS])
    return folder


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
    assert list(row) == EVAL_ROW_FIELDS
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


def test_citations_are_counted_against_the_minimum():
    question = {"id": "q", "min_citations": 2}
    few = make_record(checks={**CLEAN_CHECKS, "cited_review_ids": [1]})
    enough = make_record(checks={**CLEAN_CHECKS, "cited_review_ids": [1, 2]})
    assert score_question(question, few)["citations_ok"] is False
    assert score_question(question, enough)["citations_ok"] is True


def fake_trend(aspect=None, granularity="month", periods=3):
    return {"series": [
        {"period": "2023-01", "n_reviews": 0, "net_sentiment": 0, "pct": {"positive": 0, "negative": 0}},
        {"period": "2023-02", "n_reviews": 10, "net_sentiment": 77.1, "pct": {"positive": 85.0, "negative": 7.9}},
    ]}


def fake_report(window_days=30):
    return {
        "overall": {"n_reviews": 30, "net_sentiment": 77.1},
        "aspects": [
            {"aspect": "price", "current": {"net_sentiment": 50.0, "n_reviews": 4}},
            {"aspect": "texture_effectiveness", "current": {"net_sentiment": 20.0, "n_reviews": 5}},
            {"aspect": "availability", "current": {"net_sentiment": -90.0, "n_reviews": 0}},
        ],
    }


def fake_flagged(**kwargs):
    if kwargs.get("issue_type") == "quality":
        return {"total_matches": 2, "reviews": [
            {"review_id": 8, "product_name": "Pump Jar"}, {"review_id": 9, "product_name": "Pump Jar"},
        ]}
    return {"total_matches": 1, "reviews": [{"review_id": 7, "product_name": "Glow Serum"}]}


@pytest.fixture
def fake_tools(monkeypatch):
    monkeypatch.setattr(eval_questions, "sentiment_trend", fake_trend)
    monkeypatch.setattr(eval_questions, "generate_summary_report", fake_report)
    monkeypatch.setattr(eval_questions, "flagged_reviews", fake_flagged)


def test_month_groups_skip_months_without_reviews(fake_tools):
    groups = eval_questions.month_groups("packaging")
    assert len(groups) == 1
    assert "77.1" in groups[0]
    assert "85" in groups[0]


def test_lowest_aspect_ignores_aspects_without_reviews(fake_tools):
    assert eval_questions.lowest_aspect() == ["texture_effectiveness", "texture effectiveness"]


def test_build_questions_uses_the_real_numbers(fake_tools):
    questions = eval_questions.build_questions()
    by_id = {question["id"]: question for question in questions}
    assert len(questions) == 13
    assert len(by_id) == 13
    assert by_id["flagged_high"]["facts"] == [["7", "R7"]]
    assert by_id["followup_product"]["facts"] == [["glow"]]
    assert by_id["flagged_quality"]["facts"] == [["2", "8", "9"]]
    assert by_id["summary_30"]["facts"] == [["30"], ["77", "77.1"]]
    assert by_id["trend_packaging"]["min_facts"] == 1
    assert by_id["role_limit"]["role"] == "support_team"


def test_run_pair_scores_every_question(fake_agent):
    rows = run_evaluation.run_pair("model-a", QUESTIONS)
    agent = fake_agent.instances[0]
    assert [row["id"] for row in rows] == ["q1", "q2", "q3"]
    assert all(row["passed"] for row in rows)
    assert rows[0]["framework"] == "langgraph"
    assert rows[0]["model"] == "model-a"
    assert agent.asked[0][2] == agent.asked[1][2]
    assert agent.asked[0][2] != agent.asked[2][2]
    assert agent.asked[1][1] == "support_team"
    assert agent.closed is True


def test_run_pair_marks_every_question_failed_when_the_agent_cannot_start(fake_agent):
    fake_agent.start_error = AssistantUnavailableError()
    rows = run_evaluation.run_pair("model-a", QUESTIONS)
    assert len(rows) == 3
    assert all(row["status"] == "error" and row["passed"] is False for row in rows)
    assert fake_agent.instances[0].closed is True


def test_run_pair_keeps_going_after_one_question_fails(fake_agent):
    fake_agent.fail_question = "Second question?"
    rows = run_evaluation.run_pair("model-a", QUESTIONS)
    assert rows[1]["status"] == "error"
    assert rows[1]["answer"].startswith("RuntimeError: boom")
    assert rows[0]["passed"] is True
    assert rows[2]["passed"] is True
    assert fake_agent.instances[0].closed is True


def test_run_writes_the_results_and_the_summary(fake_agent, eval_paths):
    run_evaluation.run(["model-a"])
    results = pd.read_csv(eval_paths / "results.csv")
    summary = pd.read_csv(eval_paths / "summary.csv")
    assert len(results) == 3
    assert summary.loc[0, "questions"] == 3
    assert summary.loc[0, "pass_rate_pct"] == 100.0


def test_run_uses_the_default_model(fake_agent, eval_paths):
    run_evaluation.run()
    assert fake_agent.instances[0].model == DEFAULT_MODEL


def test_run_rejects_unknown_question_ids(fake_agent, eval_paths):
    with pytest.raises(SystemExit):
        run_evaluation.run(["model-a"], ids=["no-such-question"])


def test_run_can_limit_the_questions(fake_agent, eval_paths):
    run_evaluation.run(["model-a"], ids=["q1"])
    assert len(pd.read_csv(eval_paths / "results.csv")) == 1


def test_run_replaces_the_old_row_of_a_question_it_runs_again(fake_agent, eval_paths):
    run_evaluation.run(["model-a"])
    run_evaluation.run(["model-a"], ids=["q1"])
    assert len(pd.read_csv(eval_paths / "results.csv")) == 3


def test_run_keeps_one_row_per_model_and_question(fake_agent, eval_paths):
    run_evaluation.run(["model-a", "model-b"])
    results = pd.read_csv(eval_paths / "results.csv")
    summary = pd.read_csv(eval_paths / "summary.csv")
    assert len(results) == 6
    assert len(summary) == 2


def test_run_drops_results_from_another_framework(fake_agent, eval_paths):
    eval_paths.mkdir(parents=True)
    old = pd.DataFrame([{"framework": "other", "model": "model-a", "id": "old-question", "status": "answered"}])
    old.to_csv(eval_paths / "results.csv", index=False)
    run_evaluation.run(["model-a"])
    results = pd.read_csv(eval_paths / "results.csv")
    assert "old-question" not in set(results["id"])

