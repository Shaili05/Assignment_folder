"""
input_checks.py

Input checks that run before any model call.

check_question decides whether a question can be answered from reviews:
  ok            answer it
  clarify       too broad, ask the user which aspect, product or period
  out_of_scope  needs information reviews do not contain (policies, offers)
  blocked       tries to change the assistant's instructions
  privacy       asks for a reviewer's identity, which was scrubbed from the data

looks_like_injection marks review text that reads like an instruction to the
model. Review text is always treated as data, this flag only makes it visible.
"""

import logging
import re

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


def looks_like_injection(text):
    if not isinstance(text, str):
        return False
    return bool(INJECTION_REGEX.search(text))


def reject(status, message):
    logger.info("Question stopped by input checks: status=%s", status)
    return {"status": status, "message": message}


def check_question(question):
    if not isinstance(question, str) or not question.strip():
        return reject("clarify", CLARIFY_MESSAGE)
    if looks_like_injection(question):
        return reject("blocked", BLOCKED_MESSAGE)
    if PRIVACY_REGEX.search(question):
        return reject("privacy", PRIVACY_MESSAGE)
    if OUT_OF_SCOPE_REGEX.search(question):
        return reject("out_of_scope", OUT_OF_SCOPE_MESSAGE)
    if not TOPIC_REGEX.search(question):
        return reject("clarify", CLARIFY_MESSAGE)
    return {"status": "ok", "message": ""}


