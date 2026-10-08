from src.data_prep.label_rules import rating_to_sentiment, rule_aspects


def test_rating_to_sentiment_negative():
    assert rating_to_sentiment(1) == "negative"
    assert rating_to_sentiment(2) == "negative"


def test_rating_to_sentiment_neutral():
    assert rating_to_sentiment(3) == "neutral"


def test_rating_to_sentiment_positive():
    assert rating_to_sentiment(4) == "positive"
    assert rating_to_sentiment(5) == "positive"


def test_texture_effectiveness_always_present():
    result = rule_aspects("This is a plain review with no special keywords.")
    assert "texture_effectiveness" in result


def test_packaging_keyword_detected():
    result = rule_aspects("The pump on this bottle keeps leaking.")
    assert "packaging" in result


def test_price_keyword_detected():
    result = rule_aspects("Way too expensive for what you get.")
    assert "price" in result


def test_availability_keyword_detected():
    result = rule_aspects("Sold out everywhere, impossible to find.")
    assert "availability" in result


def test_non_string_input_returns_general():
    assert rule_aspects(None) == "general"
