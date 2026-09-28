"""
label_rules.py

Rule-based sentiment and aspect labels.

Sentiment follows the star rating (1-2 negative, 3 neutral, 4-5 positive).
On the hand-checked gold set this scored far higher than the local
DistilBERT sentiment model.

Aspects come from keyword rules. texture_effectiveness is the default aspect
because almost every review talks about how the product works or feels. The
other three aspects are added when their keywords appear.
"""

import re

PRICE_PATTERN = re.compile(
    r"\bpric\w*|\bexpensive\b|\bcheap\w*|\bworth\b|\bcost\w*|\bmoney\b|\bafford\w*"
    r"|\bvalue\b|\bbargain\b|\bsplurge\b|\bpenny\b|\bbudget\b|\bbucks?\b|\bdollars?\b|\$\s?\d",
    re.I,
)

PACKAGING_PATTERN = re.compile(
    r"\bpump\b|\bbottles?\b|\bjars?\b|\btubes?\b|\bpackag\w*|\bcontainers?\b|\bcap\b|\blid\b"
    r"|\bdispens\w*|\bleak\w*|\bseal\w*|\brefill\w*|\bsqueez\w*|\bdropper\b|\bapplicator\b"
    r"|\bpackets?\b|\bspout\b|\bnozzle\b",
    re.I,
)

AVAILABILITY_PATTERN = re.compile(
    r"\bsold out\b|\bout of stock\b|\brestock\w*|\bdiscontinued\b|\bhard to find\b"
    r"|\bback ?order\w*|\bcan'?t find\b|\bno longer (?:available|sold|made)\b"
    r"|\bnot available\b|\bunavailable\b",
    re.I,
)

ASPECT_ORDER = ["packaging", "price", "texture_effectiveness", "availability"]


def rating_to_sentiment(rating):
    if rating <= 2:
        return "negative"
    if rating == 3:
        return "neutral"
    return "positive"


def rule_aspects(text):
    found = {"texture_effectiveness"}
    if not isinstance(text, str):
        return "general"
    if PRICE_PATTERN.search(text):
        found.add("price")
    if PACKAGING_PATTERN.search(text):
        found.add("packaging")
    if AVAILABILITY_PATTERN.search(text):
        found.add("availability")
    return ", ".join(a for a in ASPECT_ORDER if a in found)


