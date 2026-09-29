"""
grounding.py

Checks run on every answer after the model replies: are the cited review ids,
quoted phrases and numbers backed by what the tools actually returned?
"""

import json
import logging
import re

from src.config.constants import MIN_QUOTE_CHARS
from src.guardrails.input_checks import looks_like_injection

logger = logging.getLogger(__name__)

CITATION_REGEX = re.compile(r"\[R(\d+)\]")
QUOTE_REGEX = re.compile(r"[\u201c\"]([^\u201d\"]{12,}?)[\u201d\"]")
NUMBER_REGEX = re.compile(r"-?\d+(?:\.\d+)?")
DATE_REGEX = re.compile(r"\d{4}-\d{2}(?:-\d{2})?")
YEAR_REGEX = re.compile(r"\b(?:19|20)\d{2}\b")
DASHES = "\u2010\u2011\u2012\u2013\u2014\u2212"
SMALL_INTEGERS = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}
NUMBER_TOLERANCE = 0.51


def normalize_text(text):
    text = text.lower().replace("*", "")
    for old, new in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u2013", "-"), ("\u2014", "-")):
        text = text.replace(old, new)
    return " ".join(text.split())


def unsupported_quotes(answer, reviews):
    corpus = normalize_text(" ".join(str(r["review_text"]) for r in reviews))
    missing = []
    for quote in QUOTE_REGEX.findall(answer):
        for fragment in re.split(r"\u2026|\.\.\.", quote):
            fragment = normalize_text(fragment).strip(" .,;:!?-\"'")
            if len(fragment) >= MIN_QUOTE_CHARS and fragment not in corpus:
                missing.append(fragment)
    return missing


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
    checks = {
        "cited_review_ids": cited,
        "invalid_citations": [c for c in cited if c not in reviews],
        "unsupported_quotes": unsupported_quotes(answer, texts) if texts else [],
        "unsupported_numbers": unsupported_numbers(answer, question, tool_calls),
        "injection_detected": any(
            r.get("instruction_like") or looks_like_injection(r.get("review_text", "")) for r in reviews.values()
        ),
        "evidence_review_ids": sorted(reviews),
    }
    problems = {k: len(checks[k]) for k in ("invalid_citations", "unsupported_quotes", "unsupported_numbers") if checks[k]}
    if problems:
        logger.warning("Grounding problems in an answer: %s", problems)
    if checks["injection_detected"]:
        logger.warning("Instruction-like text found in retrieved reviews.")
    return checks


