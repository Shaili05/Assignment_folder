import logging
import re

from src.agents.roles import allowed_tools, can_call
from src.config.constants import (
    ROLE_GATE_MESSAGE, ROLE_GATE_RULES, ROLE_GATE_STATUS, ROLE_LABELS, TOOL_LABELS,
)

logger = logging.getLogger(__name__)

INJECTION_PATTERNS = [
    r"ignore (?:all |any |the |your )?(?:previous|prior|above|earlier)?\s?(?:instructions|prompts?|rules|guidelines)",
    r"disregard (?:all |any |the |your )?(?:previous|prior|above)?\s?(?:instructions|rules|guidelines)",
    r"(?:reveal|print|show|repeat|output|leak) (?:your |the )?(?:system|hidden|initial|secret) (?:prompt|instructions)",
    r"\bsystem prompt\b",
    r"\bapi[_ ]?keys?\b",
    r"\bnew instructions?\s*:",
    r"\b(?:reply|respond|answer) only with\b",
    r"\bforget (?:everything|all|your)\b",
    r"\boverride (?:your|the) (?:instructions|rules|guidelines)\b",
    r"\bdo not answer the question\b",
]
INJECTION_REGEX = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)

OUT_OF_SCOPE_REGEX = re.compile(
    r"\b(?:return|refund|exchange)s?\s+(?:policy|policies|window|period|process)\b"
    r"|\bwarranty\b|\bcoupon\b|\bpromo(?:tion)?\s+code\b|\bdiscount\s+code\b"
    r"|\bcustomer\s+(?:service|support)\b|\bstore\s+hours\b",
    re.IGNORECASE,
)

PRIVACY_REGEX = re.compile(
    r"\b(?:reviewer'?s?|customer'?s?|user'?s?)\s+(?:name|email|phone|address|identity|personal|contact)\b"
    r"|\bwho (?:wrote|left|posted|submitted)\b[^.?!]*\breview\b"
    r"|\breal name\b|\bemail address\b|\bphone number\b|\bidentify the reviewer\b",
    re.IGNORECASE,
)

TOPIC_REGEX = re.compile(
    r"packag|bottle|pump|jar\b|tube\b|pric|cost|expens|cheap|worth|value|textur|scent|smell|fragrance"
    r"|effective|effect|result|skin|acne|breakout|dry|oily|irritat|reaction|rash|burn|sting|allerg"
    r"|safe|danger|mold|expired|leak|quality|defect|availab|stock|shipping|deliver"
    r"|sentiment|complain|praise|feedback|recommend|negative|positive|satisf|issue|problem|concern"
    r"|trend|report|summar|compar|flagged|severity|repurchase|moistur|clean|sunscreen|cream|serum",
    re.IGNORECASE,
)

CLARIFY_MESSAGE = (
    '''That question is too broad for me to answer reliably. Which aspect should I look at
    (packaging, price, texture and effectiveness, availability, or safety issues), and for which
    product, brand or time period?'''
)
OUT_OF_SCOPE_MESSAGE = (
    '''Customer reviews do not contain official policies such as returns, refunds, warranties or
    promotions, so I cannot answer that from this data. Please check the brand or retailer directly.'''
)
BLOCKED_MESSAGE = (
    """I can only help with questions about the review data, so I won't follow instructions that try
    to change how I work. What would you like to know about the reviews?"""
)
PRIVACY_MESSAGE = (
    """Reviewer names, emails and other identifying details were removed before this data was loaded,
    so I have none to share. I can still help with what the reviews themselves say."""
)


def matches_injection_pattern(text):
    if not isinstance(text, str):
        return False
    return bool(INJECTION_REGEX.search(text))


def reject(status, message):
    logger.info("Question stopped by input checks: status=%s", status)
    return {"status": status, "message": message}


def check_question(question):
    if not isinstance(question, str) or not question.strip():
        return reject("clarify", CLARIFY_MESSAGE)
    if matches_injection_pattern(question):
        return reject("blocked", BLOCKED_MESSAGE)
    if PRIVACY_REGEX.search(question):
        return reject("privacy", PRIVACY_MESSAGE)
    if OUT_OF_SCOPE_REGEX.search(question):
        return reject("out_of_scope", OUT_OF_SCOPE_MESSAGE)
    if not TOPIC_REGEX.search(question):
        return reject("clarify", CLARIFY_MESSAGE)
    return {"status": "ok", "message": ""}


def join_words(items):
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def check_role_access(question, role):
    if not isinstance(question, str):
        return None
    for tool, rule in ROLE_GATE_RULES.items():
        if rule["pattern"].search(question) and not can_call(role, tool):
            allowed_roles = [label for name, label in ROLE_LABELS.items() if can_call(name, tool)]
            can_do = [TOOL_LABELS.get(name, name).lower() for name in allowed_tools(role)]
            message = ROLE_GATE_MESSAGE.format(
                feature=rule["feature"], allowed_roles=join_words(allowed_roles),
                role_label=ROLE_LABELS[role], can_do=join_words(can_do),
            )
            return reject(ROLE_GATE_STATUS, message)
    return None
