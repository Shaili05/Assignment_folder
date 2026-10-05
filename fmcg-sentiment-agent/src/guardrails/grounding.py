import json
import logging
import re

from src.config.constants import MIN_QUOTE_CHARS, NUMBER_TOLERANCE, SMALL_INTEGERS
from src.guardrails.input_checks import matches_injection_pattern

logger = logging.getLogger(__name__)

CITATION_REGEX = re.compile(r"\[R(\d+)\]")
QUOTE_REGEX = re.compile(rf"[\u201c\"]([^\u201d\"]{{{MIN_QUOTE_CHARS},}}?)[\u201d\"]")
NUMBER_REGEX = re.compile(r"-?\d+(?:\.\d+)?")
DATE_REGEX = re.compile(r"\d{4}-\d{2}(?:-\d{2})?")
YEAR_REGEX = re.compile(r"\b(?:19|20)\d{2}\b")
ELLIPSIS_REGEX = re.compile(r"\u2026|\.\.\.")
DASHES = "\u2010\u2011\u2012\u2013\u2014\u2212"
FRAGMENT_EDGE_CHARS = " .,;:!?-\"'"
TEXT_REPLACEMENTS = (
    ("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u2013", "-"), ("\u2014", "-"),
)
GROUNDING_PROBLEM_KEYS = ("invalid_citations", "unsupported_quotes", "unsupported_numbers")


def normalize_text(text):
    text = text.lower().replace("*", "")
    for old, new in TEXT_REPLACEMENTS:
        text = text.replace(old, new)
    return " ".join(text.split())


def quote_fragments(quote):
    for fragment in ELLIPSIS_REGEX.split(quote):
        yield normalize_text(fragment).strip(FRAGMENT_EDGE_CHARS)


def unsupported_quotes(answer, reviews):
    corpus = normalize_text(" ".join(str(r["review_text"]) for r in reviews))
    missing = []
    for quote in QUOTE_REGEX.findall(answer):
        for fragment in quote_fragments(quote):
            if len(fragment) >= MIN_QUOTE_CHARS and fragment not in corpus:
                missing.append(fragment)
    return missing


def parse_json(text):
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None


def reviews_in_tool_data(data):
    found = list(data.get("reviews", []))
    if isinstance(data.get("flagged"), dict):
        found += data["flagged"].get("reviews", [])
    return found


def collect_reviews(tool_calls):
    reviews = {}
    for call in tool_calls:
        data = parse_json(call.get("output_text"))
        if not isinstance(data, dict):
            continue
        for review in reviews_in_tool_data(data):
            if "review_id" in review:
                reviews[int(review["review_id"])] = review
    return reviews


def cited_review_ids(answer):
    cited = []
    for match in CITATION_REGEX.findall(answer):
        if int(match) not in cited:
            cited.append(int(match))
    return cited


def strip_dates(text):
    for dash in DASHES:
        text = text.replace(dash, "-")
    text = DATE_REGEX.sub(" ", text)
    return YEAR_REGEX.sub(" ", text)


def numbers_in(text):
    return NUMBER_REGEX.findall(strip_dates(CITATION_REGEX.sub(" ", text)))


def allowed_numbers(question, tool_calls):
    tool_text = " ".join(str(call.get("output_text", "")) for call in tool_calls)
    source = tool_text + " " + question
    return [float(n) for n in NUMBER_REGEX.findall(strip_dates(source))]


def matches_any_allowed(value, allowed):
    return any(abs(value - a) <= NUMBER_TOLERANCE for a in allowed)


def unsupported_numbers(answer, question, tool_calls):
    if not tool_calls:
        return []
    allowed = allowed_numbers(question, tool_calls)
    missing = []
    for token in numbers_in(answer):
        if token in SMALL_INTEGERS:
            continue
        if not matches_any_allowed(float(token), allowed):
            missing.append(token)
    return missing


def is_injection_like(review):
    return bool(review.get("instruction_like") or matches_injection_pattern(review.get("review_text", "")))


def check_grounding(answer, question, tool_calls, previous_reviews=None):
    reviews = {**(previous_reviews or {}), **collect_reviews(tool_calls)}
    cited = cited_review_ids(answer)
    texts = [{"review_text": r.get("review_text", "")} for r in reviews.values()]
    checks = {
        "cited_review_ids": cited,
        "invalid_citations": [c for c in cited if c not in reviews],
        "unsupported_quotes": unsupported_quotes(answer, texts) if texts else [],
        "unsupported_numbers": unsupported_numbers(answer, question, tool_calls),
        "injection_detected": any(is_injection_like(r) for r in reviews.values()),
        "evidence_review_ids": sorted(reviews),
    }
    problems = {key: len(checks[key]) for key in GROUNDING_PROBLEM_KEYS if checks[key]}
    if problems:
        logger.warning("Grounding problems in an answer: %s", problems)
    if checks["injection_detected"]:
        logger.warning("Instruction-like text found in retrieved reviews.")
    return checks


