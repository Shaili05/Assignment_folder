"""
agent_core.py


Framework-independent part of one agent turn:
  input guardrails -> backend call -> grounding checks -> audit log entry.
"""


import json
import re
import time


from src.agents.audit import log_interaction
from src.rag.generator import unsupported_quotes
from src.rag.guardrails import check_question, looks_like_injection


CITATION_REGEX = re.compile(r"\[R(\d+)\]")
NUMBER_REGEX = re.compile(r"-?\d+(?:\.\d+)?")
DATE_REGEX = re.compile(r"\d{4}-\d{2}(?:-\d{2})?")
YEAR_REGEX = re.compile(r"\b(?:19|20)\d{2}\b")
DASHES = "\u2010\u2011\u2012\u2013\u2014\u2212"
SMALL_INTEGERS = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}
NUMBER_TOLERANCE = 0.51




def precheck(question, has_history):
    check = check_question(question)
    if check["status"] == "clarify" and has_history:
        return {"status": "ok", "message": ""}
    return check




def parse_json(text):
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None




def collect_reviews(tool_calls):
    reviews = {}
    for call in tool_calls:
        data = parse_json(call.get("output_text"))
        if not isinstance(data, dict):
            continue
        found = list(data.get("reviews", []))
        if isinstance(data.get("flagged"), dict):
            found += data["flagged"].get("reviews", [])
        for review in found:
            if "review_id" in review:
                reviews[int(review["review_id"])] = review
    return reviews




def strip_dates(text):
    for dash in DASHES:
        text = text.replace(dash, "-")
    text = DATE_REGEX.sub(" ", text)
    return YEAR_REGEX.sub(" ", text)




def numbers_in(text):
    return NUMBER_REGEX.findall(strip_dates(CITATION_REGEX.sub(" ", text)))




def unsupported_numbers(answer, question, tool_calls):
    if not tool_calls:
        return []
    source = " ".join(str(call.get("output_text", "")) for call in tool_calls) + " " + question
    allowed = [float(n) for n in NUMBER_REGEX.findall(strip_dates(source))]
    missing = []
    for token in numbers_in(answer):
        if token in SMALL_INTEGERS:
            continue
        value = float(token)
        if not any(abs(value - a) <= NUMBER_TOLERANCE for a in allowed):
            missing.append(token)
    return missing




def check_grounding(answer, question, tool_calls, previous_reviews=None):
    reviews = {**(previous_reviews or {}), **collect_reviews(tool_calls)}
    cited = []
    for match in CITATION_REGEX.findall(answer):
        if int(match) not in cited:
            cited.append(int(match))
    texts = [{"review_text": r.get("review_text", "")} for r in reviews.values()]
    return {
        "cited_review_ids": cited,
        "invalid_citations": [c for c in cited if c not in reviews],
        "unsupported_quotes": unsupported_quotes(answer, texts) if texts else [],
        "unsupported_numbers": unsupported_numbers(answer, question, tool_calls),
        "injection_detected": any(
            r.get("instruction_like") or looks_like_injection(r.get("review_text", "")) for r in reviews.values()
        ),
        "evidence_review_ids": sorted(reviews),
    }




def audit_copy(record):
    entry = {k: v for k, v in record.items() if k != "tool_calls"}
    entry["tool_calls"] = [
        {"name": c["name"], "arguments": c["arguments"], "output_chars": len(c.get("output_text") or "")}
        for c in record.get("tool_calls", [])
    ]
    return entry




async def run_turn(backend, question, role, session_id, turn_counts, model_spec, audit_path=None,
                   session_reviews=None):
    session_reviews = session_reviews if session_reviews is not None else {}
    base = {
        "session_id": session_id, "role": role, "framework": backend.name,
        "model": model_spec, "question": question,
    }
    check = precheck(question, turn_counts.get(session_id, 0) > 0)
    if check["status"] != "ok":
        record = {**base, "status": check["status"], "answer": check["message"], "tool_calls": [],
                  "prompt_tokens": 0, "completion_tokens": 0, "latency_sec": 0.0, "checks": {}}
        record["interaction_id"] = log_interaction(audit_copy(record), audit_path)["interaction_id"]
        return record


    started = time.time()
    try:
        raw = await backend.ask(question, role, session_id)
    except Exception as exc:
        record = {**base, "status": "error", "answer": f"The assistant hit an error: {exc}", "tool_calls": [],
                  "prompt_tokens": 0, "completion_tokens": 0,
                  "latency_sec": round(time.time() - started, 2), "checks": {}}
        record["interaction_id"] = log_interaction(audit_copy(record), audit_path)["interaction_id"]
        return record


    turn_counts[session_id] = turn_counts.get(session_id, 0) + 1
    previous = session_reviews.get(session_id, {})
    checks = check_grounding(raw["answer"], question, raw["tool_calls"], previous)
    session_reviews[session_id] = {**previous, **collect_reviews(raw["tool_calls"])}
    record = {
        **base, "status": "answered", "answer": raw["answer"], "tool_calls": raw["tool_calls"],
        "prompt_tokens": raw["prompt_tokens"], "completion_tokens": raw["completion_tokens"],
        "latency_sec": round(time.time() - started, 2), "checks": checks,
    }
    entry = log_interaction(audit_copy(record), audit_path)
    record["interaction_id"] = entry["interaction_id"]
    record["cost_usd"] = entry.get("cost_usd")
    return record



