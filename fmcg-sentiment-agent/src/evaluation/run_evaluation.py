"""
run_evaluation.py

Runs the test questions through each (framework, model) pair and scores every
answer automatically:

  status    the expected outcome (answered, clarify, out_of_scope, blocked)
  tool      the right tool was called, and no forbidden tool
  facts     the numbers and ids computed from the data appear in the answer
  grounded  no invalid citations and no quotes missing from the reviews
  passed    all of the above

Results go to data/evaluation/results.csv and summary.csv. Running a pair
again replaces its old rows. The dashboard Evaluation tab reads these files.

Run:
    python src/evaluation/run_evaluation.py --frameworks langgraph --models groq:openai/gpt-oss-120b
    python src/evaluation/run_evaluation.py --frameworks langgraph autogen --models groq:openai/gpt-oss-120b groq:openai/gpt-oss-20b groq:qwen/qwen3.8-27b
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.audit import new_session_id
from agent.runtime import AgentRuntime
from evaluation.test_questions import build_questions, matches

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "data" / "evaluation"
RESULTS_PATH = OUTPUT_DIR / "results.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary.csv"
AUDIT_PATH = REPO_ROOT / "logs" / "evaluation_audit.jsonl"

# Every row written to results.csv has exactly these keys, in this order,
# whether the question was scored normally or failed outright. Keeping one
# fixed set of columns is what stops a partial row from breaking the CSV.
ROW_FIELDS = [
    "status", "passed", "status_ok", "tool_ok", "facts_ok", "citations_ok", "grounded_ok",
    "unsupported_numbers", "invalid_citations", "unsupported_quotes", "tool_call_count",
    "tools_called", "latency_sec", "prompt_tokens", "completion_tokens", "cost_usd", "answer",
]


def score_question(question, record):
    answer = record.get("answer", "")
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
        "answer": answer.replace("\n", " ")[:600],
    }
    return {field: row[field] for field in ROW_FIELDS}


def failed_row(message):
    row = {
        "status": "error", "passed": False, "status_ok": False, "tool_ok": False, "facts_ok": False,
        "citations_ok": False, "grounded_ok": False, "unsupported_numbers": 0,
        "invalid_citations": "", "unsupported_quotes": "", "tool_call_count": 0, "tools_called": "",
        "latency_sec": 0.0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0,
        "answer": message[:600],
    }
    return {field: row[field] for field in ROW_FIELDS}


def run_pair(framework, model, questions):
    print(f"{framework} / {model}: starting the agent", flush=True)
    runtime = AgentRuntime(framework, model, audit_path=AUDIT_PATH)
    rows = []
    try:
        runtime.wait_until_ready()
    except RuntimeError as exc:
        print(f"  could not start: {exc}", flush=True)
        return [{"framework": framework, "model": model, "id": q["id"], "question": q["question"],
                 **failed_row(str(exc))} for q in questions]

    sessions = {}
    try:
        for question in questions:
            session_id = sessions.setdefault(question["session"], new_session_id())
            try:
                record = runtime.ask(question["question"], question.get("role", "brand_manager"), session_id)
                scored = score_question(question, record)
            except Exception as exc:
                scored = failed_row(f"{exc.__class__.__name__}: {exc}")
            rows.append({"framework": framework, "model": model, "id": question["id"],
                         "question": question["question"], **scored})
            print(f"  {question['id']}: {'PASS' if scored['passed'] else 'FAIL'} ({scored['status']})", flush=True)
    finally:
        runtime.close()
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frameworks", nargs="+", default=["langgraph"], choices=["langgraph", "autogen"])
    ap.add_argument("--models", nargs="+", default=["groq:openai/gpt-oss-120b"])
    args = ap.parse_args()

    questions = build_questions()
    print(f"{len(questions)} questions, {len(args.frameworks) * len(args.models)} pairs to run", flush=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = pd.read_csv(RESULTS_PATH) if RESULTS_PATH.exists() else pd.DataFrame()

    for framework in args.frameworks:
        for model in args.models:
            rows = run_pair(framework, model, questions)
            if not results.empty:
                keep = ~((results["framework"] == framework) & (results["model"] == model))
                results = results[keep]
            results = pd.concat([results, pd.DataFrame(rows)], ignore_index=True)
            results.to_csv(RESULTS_PATH, index=False)
            summarize(results).to_csv(SUMMARY_PATH, index=False)

    summary = summarize(results)
    print()
    print(summary.to_string(index=False))
    best = summary.iloc[0]
    print()
    print(f"Best so far: {best['framework']} with {best['model']} ({best['pass_rate_pct']}% passed, "
          f"{best['avg_latency_s']}s average)")
    print(f"Wrote {RESULTS_PATH} and {SUMMARY_PATH}")


if __name__ == "__main__":
    main()


