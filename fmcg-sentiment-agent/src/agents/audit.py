"""
audit.py

Append-only audit log (one JSON object per line) with per-request latency,
token counts and estimated cost, plus a usage summary.

Brand managers read the full log. Other roles only see a redacted view of
their own session: time, question and status, without answers, tool
arguments, tokens or cost.

Run:
    python -m src.agents.audit --summary
"""

import argparse
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.agents.roles import audit_access
from src.config.settings import LOGS_DIR

logger = logging.getLogger(__name__)

AUDIT_PATH = LOGS_DIR / "audit_log.jsonl"

# USD per 1M tokens as (input, output). Check the provider pricing page before quoting these.
PRICES = {
    "groq:openai/gpt-oss-120b": (0.15, 0.60),
    "groq:openai/gpt-oss-20b": (0.075, 0.30),
}

REDACTED_FIELDS = ["timestamp", "session_id", "role", "question", "status"]


def new_session_id():
    return uuid.uuid4().hex[:10]


def estimate_cost(model, prompt_tokens, completion_tokens):
    if model.startswith("openrouter:") and model.endswith(":free"):
        return 0.0
    prices = PRICES.get(model)
    if not prices:
        return None
    return round((prompt_tokens * prices[0] + completion_tokens * prices[1]) / 1_000_000, 6)


def log_interaction(record, path=None):
    path = Path(path or AUDIT_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = dict(record)
    entry.setdefault("interaction_id", uuid.uuid4().hex[:12])
    entry["timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if "cost_usd" not in entry and entry.get("model"):
        entry["cost_usd"] = estimate_cost(
            entry["model"], entry.get("prompt_tokens", 0), entry.get("completion_tokens", 0)
        )

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, default=str) + "\n")
    logger.info("Logged interaction %s (status=%s)", entry["interaction_id"], entry.get("status"))
    return entry


def load_log(path=None):
    path = Path(path or AUDIT_PATH)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_log(role, session_id=None, path=None):
    records = load_log(path)
    if audit_access(role) == "full":
        return records
    own = [r for r in records if session_id and r.get("session_id") == session_id]
    return [{k: r.get(k) for k in REDACTED_FIELDS} for r in own]


def usage_summary(records):
    rows = []
    frame = pd.DataFrame([r for r in records if r.get("model")])
    if frame.empty:
        return pd.DataFrame(columns=["framework", "model", "requests", "avg_latency_s", "p95_latency_s",
                                     "prompt_tokens", "completion_tokens", "cost_usd"])
    for col in ["framework"]:
        if col not in frame:
            frame[col] = ""
        frame[col] = frame[col].fillna("")
    for col in ["latency_sec", "prompt_tokens", "completion_tokens"]:
        if col not in frame:
            frame[col] = 0
        frame[col] = frame[col].fillna(0)
    if "cost_usd" not in frame:
        frame["cost_usd"] = None
    for (framework, model), group in frame.groupby(["framework", "model"]):
        costs = pd.to_numeric(group["cost_usd"], errors="coerce")
        rows.append({
            "framework": framework, "model": model, "requests": len(group),
            "avg_latency_s": round(group["latency_sec"].mean(), 2),
            "p95_latency_s": round(group["latency_sec"].quantile(0.95), 2),
            "prompt_tokens": int(group["prompt_tokens"].sum()),
            "completion_tokens": int(group["completion_tokens"].sum()),
            "cost_usd": round(float(costs.sum()), 5) if costs.notna().any() else None,
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    if args.summary:
        records = load_log()
        print(f"{len(records)} interactions in {AUDIT_PATH}")
        print(usage_summary(records).to_string(index=False))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()


