import asyncio
import json

from src.utils.progress_log import StageCallback, log_stage, read_progress


def read_stages(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_log_stage_appends_one_json_line_per_call(tmp_path):
    path = tmp_path / "progress.jsonl"
    log_stage("s1", "support_team", "question_received", "hello", path)
    log_stage("s1", "support_team", "completed", "", path)
    rows = read_stages(path)
    assert [row["stage"] for row in rows] == ["question_received", "completed"]
    assert rows[0]["session_id"] == "s1"
    assert rows[0]["role"] == "support_team"
    assert rows[0]["detail"] == "hello"
    assert "timestamp" in rows[0]


def test_log_stage_never_raises_when_the_file_cannot_be_written(tmp_path):
    entry = log_stage("s1", "brand_manager", "failed", "x", tmp_path)
    assert entry["stage"] == "failed"


def test_callback_records_model_and_tool_steps(tmp_path):
    path = tmp_path / "progress.jsonl"
    callback = StageCallback("s1", "brand_manager", path)

    async def run():
        await callback.on_chat_model_start({}, [], run_id="m1")
        await callback.on_tool_start({"name": "sentiment_trend"}, "{}", run_id="t1", name="sentiment_trend")
        await callback.on_tool_end("output", run_id="t1")
        await callback.on_chat_model_start({}, [], run_id="m2")

    asyncio.run(run())
    rows = read_stages(path)
    assert [row["stage"] for row in rows] == ["model_call", "tool_start", "tool_done", "model_call"]
    assert rows[0]["detail"] == "model call 1"
    assert rows[3]["detail"] == "model call 2"
    assert rows[1]["detail"] == "sentiment_trend"
    assert rows[2]["detail"].startswith("sentiment_trend (")


def test_callback_records_a_failed_tool(tmp_path):
    path = tmp_path / "progress.jsonl"
    callback = StageCallback("s1", "support_team", path)

    async def run():
        await callback.on_tool_start({"name": "search_reviews"}, "{}", run_id="t1")
        await callback.on_tool_error(ValueError("bad"), run_id="t1")

    asyncio.run(run())
    rows = read_stages(path)
    assert rows[1]["stage"] == "tool_failed"
    assert rows[1]["detail"] == "search_reviews: ValueError"


def test_read_progress_returns_only_the_latest_question_of_the_session(tmp_path):
    path = tmp_path / "progress.jsonl"
    log_stage("s1", "brand_manager", "question_received", "first", path)
    log_stage("s1", "brand_manager", "completed", "", path)
    log_stage("s2", "support_team", "question_received", "other session", path)
    log_stage("s1", "brand_manager", "question_received", "second", path)
    log_stage("s1", "brand_manager", "model_call", "model call 1", path)
    stages = read_progress("s1", path)
    assert [stage["stage"] for stage in stages] == ["question_received", "model_call"]
    assert stages[0]["detail"] == "second"


def test_read_progress_skips_damaged_lines_and_unknown_sessions(tmp_path):
    path = tmp_path / "progress.jsonl"
    log_stage("s1", "brand_manager", "question_received", "q", path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("{not json\n")
    assert len(read_progress("s1", path)) == 1
    assert read_progress("nobody", path) == []


def test_read_progress_without_a_file_is_empty(tmp_path):
    assert read_progress("s1", tmp_path / "missing.jsonl") == []
