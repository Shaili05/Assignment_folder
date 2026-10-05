import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path


import pandas as pd


from src.agents.roles import audit_access
from src.config.constants import (
    AUDIT_REDACTED_FIELDS, AUDIT_VIEW_FULL, FREE_MODEL_PREFIX, FREE_MODEL_SUFFIX,
    INTERACTION_ID_LENGTH, LATENCY_PERCENTILE, PRICES, SESSION_ID_LENGTH, TOKEN_PRICE_UNIT,
    USAGE_SUMMARY_COLUMNS,
)
from src.config.settings import AUDIT_LOG_PATH
from src.utils.output import write_line


logger = logging.getLogger(__name__)


def new_session_id():
    return uuid.uuid4().hex[:SESSION_ID_LENGTH]


def estimate_cost(model, prompt_tokens, completion_tokens):
    if model.startswith(FREE_MODEL_PREFIX) and model.endswith(FREE_MODEL_SUFFIX):
        return 0.0
    prices = PRICES.get(model)
    if not prices:
        return None
    return round((prompt_tokens * prices[0] + completion_tokens * prices[1]) / TOKEN_PRICE_UNIT, 6)


def log_interaction(record, path=None):
    path = Path(path or AUDIT_LOG_PATH)
    entry = dict(record)
    entry.setdefault("interaction_id", uuid.uuid4().hex[:INTERACTION_ID_LENGTH])
    entry["timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if "cost_usd" not in entry and entry.get("model"):
        entry["cost_usd"] = estimate_cost(
            entry["model"], entry.get("prompt_tokens", 0), entry.get("completion_tokens", 0)
        )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        logger.exception("Could not write audit log entry %s", entry["interaction_id"])
        return entry
    logger.info("Logged interaction %s (status=%s)", entry["interaction_id"], entry.get("status"))
    return entry


def load_log(path=None):
    path = Path(path or AUDIT_LOG_PATH)
    if not path.exists():
        return []
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning("Skipped a damaged line in the audit log")
    return records


def read_log(role, session_id=None, path=None):
    records = load_log(path)
    if audit_access(role) == AUDIT_VIEW_FULL:
        return records
    own_sessions = set(session_id.split(",")) if session_id else set()
    own = [r for r in records if r.get("session_id") in own_sessions]
    return [{k: r.get(k) for k in AUDIT_REDACTED_FIELDS} for r in own]


def usage_summary(records):
    rows = []
    frame = pd.DataFrame([r for r in records if r.get("model")])
    if frame.empty:
        return pd.DataFrame(columns=USAGE_SUMMARY_COLUMNS)
    if "framework" not in frame:
        frame["framework"] = ""
    frame["framework"] = frame["framework"].fillna("")
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
            "p95_latency_s": round(group["latency_sec"].quantile(LATENCY_PERCENTILE), 2),
            "prompt_tokens": int(group["prompt_tokens"].sum()),
            "completion_tokens": int(group["completion_tokens"].sum()),
            "cost_usd": round(float(costs.sum()), 5) if costs.notna().any() else None,
        })
    return pd.DataFrame(rows)
