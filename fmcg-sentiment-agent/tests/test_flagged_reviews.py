from src.mcp.tools.flagged_reviews import flagged_reviews, issue_excerpt


def test_returns_only_flagged_reviews(sample_reviews):
    result = flagged_reviews(df=sample_reviews)
    assert "error" not in result
    assert result["total_matches"] == 2


def test_severity_level_filter_is_a_minimum(sample_reviews):
    result = flagged_reviews(severity_level="medium", df=sample_reviews)
    assert "error" not in result
    assert result["total_matches"] == 1


def test_invalid_severity_level_returns_error(sample_reviews):
    result = flagged_reviews(severity_level="critical", df=sample_reviews)
    assert "error" in result


def test_invalid_issue_type_returns_error(sample_reviews):
    result = flagged_reviews(issue_type="not_real", df=sample_reviews)
    assert "error" in result


def test_full_text_flag_returns_untruncated_text(sample_reviews):
    result = flagged_reviews(df=sample_reviews, full_text=True)
    review = next(r for r in result["reviews"] if r["review_id"] == 1)
    assert review["review_text"] == "Caused a burning rash on my skin."


def test_issue_type_filter_keeps_only_that_type(sample_reviews):
    result = flagged_reviews(issue_type="quality", df=sample_reviews)
    assert result["total_matches"] == 1
    assert result["reviews"][0]["review_id"] == 2


def test_long_review_excerpt_is_centred_on_the_issue():
    text = "Great product. " * 40 + "Then I got a terrible rash on my face. " + "Everything else was fine. " * 40
    excerpt = issue_excerpt(text)
    assert "rash" in excerpt
    assert excerpt.startswith("...")
    assert excerpt.endswith("...")


def test_short_review_excerpt_is_unchanged():
    assert issue_excerpt("Burning rash on my arm.") == "Burning rash on my arm."


