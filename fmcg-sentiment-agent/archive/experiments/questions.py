"""
questions.py
Single source of truth for the fixed question set used across the
project -- evaluate_rag_answers.py (benchmark comparison across
models/stores) and validate_production_questions.py (final production
system check) both import from here, so the question list never drifts
out of sync between the two.
"""

QUESTIONS = [
    "What do customers most commonly complain about regarding packaging?",
    "Are customers generally happy with the price of these products?",
    "What safety concerns have customers reported about these products?",
    "How effective do customers find these products for their skin?",
    "What issues do customers report about product availability?",
    "Summarize the most common negative feedback patterns across reviews.",
    "What do customers praise most about these products?",
    "What is the return or refund policy for these products?",
    "Tell me about these products.",
    "Do customers with sensitive skin report any specific issues?",
]

