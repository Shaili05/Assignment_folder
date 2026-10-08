import logging

import pandas as pd

from src.agents.review_agent import ReviewAgent
from src.config.constants import DEFAULT_MODEL, DEFAULT_ROLE, EVAL_ANSWER_CHARS, EVAL_ROW_FIELDS
from src.config.settings import EVAL_AUDIT_PATH, EVAL_RESULTS_PATH, EVAL_SUMMARY_PATH, EVALUATION_DIR
from src.evaluation.eval_questions import build_questions, matches
from src.exceptions.exceptions import AppError
from src.utils.audit_logger import new_session_id
from src.utils.output import write_line

logger = logging.getLogger(__name__)

def score_question(question, record):
    answer = record.get("error_detail") or record.get("answer", "")
    tools = [call["name"] for call in record.get("tool_calls", [])]
    checks = record.get("checks") or {}

    status_ok = record["status"] == question.get("status", "answered")

    tool_ok = True
    if question.get("tools"):
        tool_ok = any(t in question["tools"] for t in tools)
    if question.get("forbidden_tools"):
        tool_ok = tool_ok and not any(t in question["forbidden_tools"] for t in tools)

    facts_ok = True
    groups = question.get("facts", [])
    if groups:
        hits = sum(1 for group in groups if any(matches(answer, token) for token in group))
        facts_ok = hits >= question.get("min_facts", len(groups))

    citations_ok = True
    if question.get("min_citations"):
        citations_ok = len(checks.get("cited_review_ids", [])) >= question["min_citations"]

    grounded_ok = not (checks.get("invalid_citations") or checks.get("unsupported_quotes"))

    row = {
        "status": record["status"],
        "passed": all([status_ok, tool_ok, facts_ok, citations_ok, grounded_ok]),
        "status_ok": status_ok, "tool_ok": tool_ok, "facts_ok": facts_ok,
        "citations_ok": citations_ok, "grounded_ok": grounded_ok,
        "unsupported_numbers": len(checks.get("unsupported_numbers", [])),
        "invalid_citations": ";".join(str(c) for c in checks.get("invalid_citations", [])),
        "unsupported_quotes": " | ".join(checks.get("unsupported_quotes", [])),
        "tool_call_count": len(tools),
        "tools_called": ";".join(tools),
        "latency_sec": record.get("latency_sec", 0.0),
        "prompt_tokens": record.get("prompt_tokens", 0),
        "completion_tokens": record.get("completion_tokens", 0),
        "cost_usd": record.get("cost_usd") or 0.0,
        "answer": answer.replace("\n", " ")[:EVAL_ANSWER_CHARS],
    }
    return {field: row[field] for field in EVAL_ROW_FIELDS}

def failed_row(message):
    row = {
        "status": "error", "passed": False, "status_ok": False, "tool_ok": False, "facts_ok": False,
        "citations_ok": False, "grounded_ok": False, "unsupported_numbers": 0,
        "invalid_citations": "", "unsupported_quotes": "", "tool_call_count": 0, "tools_called": "",
        "latency_sec": 0.0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0,
        "answer": message[:EVAL_ANSWER_CHARS],
    }
    return {field: row[field] for field in EVAL_ROW_FIELDS}

def run_pair(model, questions):
    write_line(f"{model}: starting the agent")
    agent = ReviewAgent(model, audit_path=EVAL_AUDIT_PATH)
    framework = agent.name
    try:
        agent.wait_until_ready()
    except AppError as exc:
        logger.error("Could not start the agent for %s: %s", model, exc.message)
        agent.close()
        return [{"framework": framework, "model": model, "id": q["id"], "question": q["question"],
                 **failed_row(exc.message)} for q in questions]

    rows = []
    sessions = {}
    try:
        for question in questions:
            session_id = sessions.setdefault(question["session"], new_session_id())
            try:
                record = agent.ask(question["question"], question.get("role", DEFAULT_ROLE), session_id)
                scored = score_question(question, record)
            except Exception as exc:
                logger.warning("Question %s failed: %s", question["id"], exc)
                scored = failed_row(f"{exc.__class__.__name__}: {exc}")
            rows.append({"framework": framework, "model": model, "id": question["id"],
                         "question": question["question"], **scored})
            write_line(f"  {question['id']}: {'PASS' if scored['passed'] else 'FAIL'} ({scored['status']})")
    finally:
        agent.close()
    return rows

def summarize(results):
    rows = []
    for (framework, model), group in results.groupby(["framework", "model"]):
        answered = group[group["status"] == "answered"]
        rows.append({
            "framework": framework,
            "model": model,
            "questions": len(group),
            "pass_rate_pct": round(100 * group["passed"].mean(), 1),
            "status_pct": round(100 * group["status_ok"].mean(), 1),
            "tool_pct": round(100 * group["tool_ok"].mean(), 1),
            "facts_pct": round(100 * group["facts_ok"].mean(), 1),
            "grounded_pct": round(100 * group["grounded_ok"].mean(), 1),
            "avg_latency_s": round(answered["latency_sec"].mean(), 2) if len(answered) else 0.0,
            "avg_prompt_tokens": int(answered["prompt_tokens"].mean()) if len(answered) else 0,
            "avg_tool_calls": round(answered["tool_call_count"].mean(), 1) if len(answered) else 0.0,
            "total_cost_usd": round(group["cost_usd"].sum(), 5),
        })
    summary = pd.DataFrame(rows)
    return summary.sort_values(["pass_rate_pct", "avg_latency_s"], ascending=[False, True]).reset_index(drop=True)

def run(models=None, ids=None):
    models = models or [DEFAULT_MODEL]
    questions = build_questions()
    if ids:
        known = {q["id"] for q in questions}
        unknown = [i for i in ids if i not in known]
        if unknown:
            raise SystemExit(f"Unknown question ids: {', '.join(unknown)}")
        questions = [q for q in questions if q["id"] in ids]
    write_line(f"{len(questions)} questions, {len(models)} model(s) to run")

    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    results = pd.read_csv(EVAL_RESULTS_PATH) if EVAL_RESULTS_PATH.exists() else pd.DataFrame()
    if not results.empty:
        results = results[results["framework"] == ReviewAgent.name]


    for model in models:
        rows = run_pair(model, questions)
        if not results.empty:
            ran = {row["id"] for row in rows}
            stale = (results["model"] == model) & results["id"].isin(ran)
            results = results[~stale]
        results = pd.concat([results, pd.DataFrame(rows)], ignore_index=True)
        results.to_csv(EVAL_RESULTS_PATH, index=False)
        summarize(results).to_csv(EVAL_SUMMARY_PATH, index=False)

    summary = summarize(results)
    best = summary.iloc[0]
    write_line("")
    write_line(summary.to_string(index=False))
    write_line("")
    write_line(f"Best so far: {best['model']} ({best['pass_rate_pct']}% passed, {best['avg_latency_s']}s average)")
    write_line(f"Wrote {EVAL_RESULTS_PATH} and {EVAL_SUMMARY_PATH}")
