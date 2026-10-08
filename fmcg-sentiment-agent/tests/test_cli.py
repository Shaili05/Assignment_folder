import json
from types import SimpleNamespace

import pandas as pd
import pytest

import src.data_prep.apply_label_rules as apply_module
import src.data_prep.build_vectorstore as build_module
import src.data_prep.recompute_safety_flags as recompute_module
import src.data_prep.scrub_pii as scrub_module
import src.evaluation.run_evaluation as evaluation_module
import src.mcp.tools.flagged_reviews as flagged_module
import src.mcp.tools.sentiment_trend as trend_module
import src.mcp.tools.summary_report as summary_module
import src.utils.audit_logger as audit_module
from src import cli


@pytest.fixture
def lines(monkeypatch):
    captured = []
    monkeypatch.setattr(cli, "write_line", captured.append)
    return captured


def run_command(argv):
    args = cli.build_parser().parse_args(argv)
    args.func(args)


def record_calls(monkeypatch, module, name):
    calls = []
    monkeypatch.setattr(module, name, lambda *args: calls.append(args))
    return calls


def test_every_command_maps_to_its_runner():
    runners = {
        "sentiment-trend": cli.run_sentiment_trend, "flagged-reviews": cli.run_flagged_reviews,
        "summary-report": cli.run_summary_report, "apply-label-rules": cli.run_apply_label_rules,
        "recompute-safety-flags": cli.run_recompute_safety_flags, "scrub-pii": cli.run_scrub_pii,
        "build-vectorstore": cli.run_build_vectorstore, "evaluate": cli.run_evaluate,
        "audit-summary": cli.run_audit_summary,
    }
    for command, runner in runners.items():
        assert cli.build_parser().parse_args([command]).func is runner


def test_a_command_is_required():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args([])


def test_an_unknown_command_is_rejected():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["no-such-command"])


def test_default_options():
    trend = cli.build_parser().parse_args(["sentiment-trend"])
    flagged = cli.build_parser().parse_args(["flagged-reviews"])
    summary = cli.build_parser().parse_args(["summary-report"])
    assert (trend.granularity, trend.periods) == ("month", 6)
    assert flagged.limit == 5
    assert (summary.days, summary.save, summary.json) == (7, False, False)


def test_sentiment_trend_prints_the_result_as_json(monkeypatch, lines):
    seen = {}

    def fake_trend(*args):
        seen["args"] = args
        return {"series": []}

    monkeypatch.setattr(trend_module, "sentiment_trend", fake_trend)
    run_command(["sentiment-trend", "--aspect", "price", "--periods", "3"])
    assert seen["args"] == ("price", None, None, "month", 3, None)
    assert json.loads(lines[0]) == {"series": []}


def test_flagged_reviews_prints_the_result_as_json(monkeypatch, lines):
    seen = {}

    def fake_flagged(level, issue_type, days, limit):
        seen["args"] = (level, issue_type, days, limit)
        return {"total_matches": 0}

    monkeypatch.setattr(flagged_module, "flagged_reviews", fake_flagged)
    run_command(["flagged-reviews", "--level", "high", "--days", "30"])
    assert seen["args"] == ("high", None, 30, 5)
    assert json.loads(lines[0]) == {"total_matches": 0}


def test_summary_report_prints_the_markdown(monkeypatch, lines):
    monkeypatch.setattr(summary_module, "generate_summary_report", lambda *args: {"markdown": "Weekly report"})
    run_command(["summary-report", "--days", "30"])
    assert lines == ["Weekly report"]


def test_summary_report_can_print_json_without_the_markdown(monkeypatch, lines):
    report = {"markdown": "Weekly report", "overall": {"n_reviews": 4}}
    monkeypatch.setattr(summary_module, "generate_summary_report", lambda *args: report)
    run_command(["summary-report", "--json"])
    assert json.loads(lines[0]) == {"overall": {"n_reviews": 4}}


def test_summary_report_can_save_the_file(monkeypatch, lines):
    monkeypatch.setattr(summary_module, "generate_summary_report", lambda *args: {"markdown": "Weekly report"})
    monkeypatch.setattr(summary_module, "save_report", lambda report: "reports/weekly.md")
    run_command(["summary-report", "--save"])
    assert lines[-1] == "Saved reports/weekly.md"


def test_summary_report_stops_on_an_error(monkeypatch, lines):
    monkeypatch.setattr(summary_module, "generate_summary_report", lambda *args: {"error": "bad window"})
    with pytest.raises(SystemExit) as stopped:
        run_command(["summary-report"])
    assert stopped.value.code == "bad window"


def test_apply_label_rules_passes_its_options(monkeypatch):
    calls = record_calls(monkeypatch, apply_module, "run")
    run_command(["apply-label-rules", "--collection", "other", "--skip-chroma"])
    assert calls[0][3:] == ("other", True)


def test_recompute_safety_flags_passes_its_options(monkeypatch):
    calls = record_calls(monkeypatch, recompute_module, "run")
    run_command(["recompute-safety-flags", "--collection", "other"])
    assert calls[0][3:] == ("other", False)


def test_scrub_pii_passes_the_file_names(monkeypatch):
    calls = record_calls(monkeypatch, scrub_module, "run")
    run_command(["scrub-pii", "--input", "in.csv", "--output", "out.csv"])
    assert calls == [("in.csv", "out.csv")]


def test_build_vectorstore_passes_its_options(monkeypatch):
    calls = record_calls(monkeypatch, build_module, "run")
    run_command(["build-vectorstore", "--scrubbed", "s.csv", "--chroma-dir", "store", "--collection", "c"])
    assert calls == [("s.csv", "store", "c")]


def test_evaluate_passes_models_and_question_ids(monkeypatch):
    calls = record_calls(monkeypatch, evaluation_module, "run")
    run_command(["evaluate", "--models", "m1", "m2", "--ids", "q1"])
    assert calls == [(["m1", "m2"], ["q1"])]


def test_audit_summary_prints_the_count_and_the_table(monkeypatch, lines):
    monkeypatch.setattr(audit_module, "load_log", lambda: [{}, {}])
    monkeypatch.setattr(audit_module, "usage_summary", lambda records: pd.DataFrame({"model": ["model-a"]}))
    run_command(["audit-summary"])
    assert lines[0] == "2 interactions"
    assert "model-a" in lines[1]

