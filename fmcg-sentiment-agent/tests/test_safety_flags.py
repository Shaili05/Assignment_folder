"""
test_safety_flags.py

Tests for src/data_prep/safety_flags.py -- the severity scoring rules that
decide whether a review gets flagged, and at what severity level.
"""

from src.data_prep.safety_flags import analyze_review


def test_five_star_review_never_flagged():
    """A 5-star review is never escalated, even if it mentions a safety word."""
    result = analyze_review("It gave me a little redness at first but then it was fine.", "positive", 5)
    assert result["is_safety_issue"] is False


def test_high_severity_safety_term_flags_correctly():
    result = analyze_review("This caused a chemical burn and I had to go to the hospital.", "negative", 1)
    assert result["is_safety_issue"] is True
    assert result["issue_type"] == "safety"
    assert result["severity_level"] == "high"


def test_negation_prevents_false_positive():
    """'no rash' should not trigger the rash flag."""
    result = analyze_review("Used it for a week, no rash, no irritation, works great.", "positive", 5)
    assert result["is_safety_issue"] is False


def test_quality_issue_detected():
    result = analyze_review("Arrived damaged, the pump was broken on delivery.", "negative", 2)
    assert result["is_safety_issue"] is True
    assert result["issue_type"] == "quality"


def test_empty_text_returns_no_issue():
    result = analyze_review("", "neutral", 3)
    assert result["is_safety_issue"] is False
    assert result["severity_level"] == "none"


def test_four_star_only_flags_high_weight_terms():
    """A 4-star review should only escalate for weight-3 (high) terms, not weak ones."""
    result = analyze_review("Slight irritation but otherwise decent.", "neutral", 4)
    assert result["is_safety_issue"] is False


