"""
safety_flags.py

Rule-based detection of safety and quality issues in review text, with a
severity score. Shared by the labeling step and the flagged-reviews tool so
both use the same logic.

Each term carries a type (safety or quality) and a weight (1 low, 2 medium,
3 high). A term is ignored when a negation word appears shortly before it
in the same clause ("no rash", "didn't burn", "non-toxic").
"""

import re

NEGATION_WORDS = {
    "no", "not", "never", "without", "nothing", "none", "zero", "non",
    "hardly", "nobody", "neither", "nor", "didnt", "dont", "doesnt", "wont",
    "wasnt", "isnt", "arent", "havent", "hasnt", "hadnt", "cant", "couldnt",
    "wouldnt",
}

NEGATION_WINDOW = 6
CLAUSE_SPLIT = re.compile(r"[.!?;,:\n]|\bbut\b|\bhowever\b|\bexcept\b")
WORD_PATTERN = re.compile(r"[a-z]+")

TERM_TABLE = [
    ("hospital_visit", "safety", 3, r"\bhospital(?!-?\s?grade)\w*|\bemergency room\b|\burgent care\b"),
    ("anaphylaxis", "safety", 3, r"\banaphyla\w*"),
    ("chemical_burn", "safety", 3, r"\bchemical burn\w*"),
    ("blistering", "safety", 3, r"\bblister\w*"),
    ("infection", "safety", 2, r"\binfect\w*"),
    ("bleeding", "safety", 3, r"\bbleeding (?:skin|sores?|cuts?|gums?)\b|\bskin bled\b|\bstarted bleeding\b|\bdrew blood\b"),
    ("toxic", "safety", 2, r"\btoxic\w*|\bpoison\w*"),
    ("contamination", "safety", 3, r"\bcontaminat\w*"),
    ("mold", "safety", 3, r"\bmou?ld(?:y|s)?\b"),
    ("expired", "quality", 3, r"\bexpired\b|\bpast (?:its |the )?expiration\b"),
    ("recall", "quality", 3, r"\bproduct recall\b|\bbeen recalled\b|\brecalled by\b|\bbatch recall\b"),
    ("allergy", "safety", 2, r"\ballerg\w*"),
    ("rash", "safety", 2, r"\brash(?:es)?\b|\bhives?\b|\bwelts?\b"),
    ("swelling", "safety", 2, r"\bswell\w*|\bswollen\b"),
    ("burning", "safety", 2, r"\bburn(?:s|ed|ing|t)?\b"),
    ("itching", "safety", 2, r"\bitch\w*"),
    ("reaction", "safety", 2, r"\breactions?\b|\breacted\b"),
    ("flare_up", "safety", 2, r"\bflare[- ]?ups?\b|\bflared up\b|\bflares up\b"),
    ("counterfeit", "quality", 2, r"\bcounterfeit\w*|\bknock-?off\b|\bnot authentic\b|\bfake (?:product|version|bottle|sephora)\b"),
    ("tampering", "quality", 2, r"\btamper\w*|\barrived open\b|\balready (?:been )?opened\b|\blooked used\b|\bseal (?:was )?(?:broken|missing|open)\b|\bunsealed\b|\bno seal\b"),
    ("spoiled", "quality", 2, r"\brancid\b|\b(?:gone|went) (?:bad|off)\b|\bsour smell\b|\bsmells? (?:off|rotten|spoiled|sour)\b"),
    ("bad_smell", "quality", 1, r"\bchemical smell\b|\bsmells? like chemicals\b"),
    ("irritation", "safety", 1, r"\birritat\w*"),
    ("stinging", "safety", 1, r"\bsting\w*"),
    ("leaking", "quality", 1, r"\bleak\w*"),
    ("damaged", "quality", 1, r"\barrived (?:damaged|broken|cracked)\b|\bdamaged (?:packaging|package|box|bottle|jar|pump|product)\b|\b(?:cap|lid|pump|seal|bottle|jar|tube|container) (?:was|is|came|arrived) (?:broken|cracked|damaged)\b|\bbroken (?:pump|cap|lid|seal|bottle|jar|tube)\b|\bshattered\b|\bdefect\w*"),
    ("separation", "quality", 1, r"\bseparat(?:ed|es|ing|ion)\b"),
    ("missing_product", "quality", 1, r"\bhalf empty\b|\bwatered down\b|\bmissing (?:the )?(?:pump|cap|lid|product|seal|box)\b"),
]

TERMS = [(label, kind, weight, re.compile(pattern)) for label, kind, weight, pattern in TERM_TABLE]

BASE_SCORE = {1: 0.25, 2: 0.5, 3: 0.75}


def is_negated(text, start):
    segment = CLAUSE_SPLIT.split(text[max(0, start - 60):start])[-1]
    words = WORD_PATTERN.findall(segment.replace("'", ""))[-NEGATION_WINDOW:]
    return any(word in NEGATION_WORDS for word in words)


def find_matches(text):
    lowered = text.lower().replace("\u2019", "'")
    found = {}
    for label, kind, weight, pattern in TERMS:
        for match in pattern.finditer(lowered):
            if not is_negated(lowered, match.start()):
                found[label] = (kind, weight)
                break
    return found


def analyze_review(text, sentiment, rating):
    empty = {
        "is_safety_issue": False,
        "issue_type": "none",
        "severity_score": 0.0,
        "severity_level": "none",
        "matched_terms": "",
    }
    if not isinstance(text, str) or not text.strip():
        return empty

    found = find_matches(text)
    if not found:
        return empty

    is_negative = sentiment == "negative"
    has_rating = rating is not None
    is_low_rating = has_rating and rating <= 2

    # The star rating is the reviewer's own verdict on the product. A 5-star
    # review is never escalated, a 4-star review only for high-weight terms.
    if has_rating and rating >= 5:
        return empty
    if has_rating and rating == 4:
        found = {label: item for label, item in found.items() if item[1] == 3}
        if not found:
            return empty

    top_weight = max(weight for _, weight in found.values())

    # Weak terms alone are only flagged when the review is negative overall.
    if top_weight == 1 and not (is_negative or is_low_rating):
        return empty

    score = BASE_SCORE[top_weight]
    score += min(0.15, 0.05 * (len(found) - 1))
    score += 0.1 if is_negative else 0.0
    score += 0.1 if is_low_rating else 0.0
    score = round(min(1.0, score), 2)

    if score >= 0.75:
        level = "high"
    elif score >= 0.5:
        level = "medium"
    else:
        level = "low"

    kinds = {kind for kind, _ in found.values()}
    if len(kinds) == 2:
        issue_type = "both"
    else:
        issue_type = kinds.pop()

    return {
        "is_safety_issue": True,
        "issue_type": issue_type,
        "severity_score": score,
        "severity_level": level,
        "matched_terms": "|".join(sorted(found)),
    }


def first_match_position(text):
    lowered = text.lower().replace("\u2019", "'")
    best = None
    for _, _, _, pattern in TERMS:
        for match in pattern.finditer(lowered):
            if not is_negated(lowered, match.start()):
                if best is None or match.start() < best:
                    best = match.start()
                break
    return best

