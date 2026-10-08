from src.data_prep.safety_flags import analyze_review


def test_five_star_review_never_flagged():
    result = analyze_review("It gave me a little redness at first but then it was fine.", "positive", 5)
    assert result["is_safety_issue"] is False


def test_high_severity_safety_term_flags_correctly():
    result = analyze_review("This caused a chemical burn and I had to go to the hospital.", "negative", 1)
    assert result["is_safety_issue"] is True
    assert result["issue_type"] == "safety"
    assert result["severity_level"] == "high"


def test_negation_prevents_false_positive():
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
    result = analyze_review("Slight irritation but otherwise decent.", "neutral", 4)
    assert result["is_safety_issue"] is False


def test_flags_on_a_five_star_review_are_ignored():
    result = analyze_review("I got a rash after using it.", "positive", 5)
    assert result["is_safety_issue"] is False


def test_weak_term_without_a_negative_signal_is_ignored():
    result = analyze_review("The pump was leaking a little.", "neutral", None)
    assert result["is_safety_issue"] is False


def test_medium_severity_level():
    result = analyze_review("I got a rash after using it.", "neutral", 3)
    assert result["severity_level"] == "medium"


def test_safety_and_quality_terms_together_give_both():
    result = analyze_review("I got a rash and the bottle arrived damaged.", "negative", 1)
    assert result["issue_type"] == "both"


