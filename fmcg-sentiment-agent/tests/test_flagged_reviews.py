"""
test_flagged_reviews.py

Tests for src/mcp/tools/flagged_reviews.py using an in-memory sample
DataFrame.
"""

from src.mcp.tools.flagged_reviews import flagged_reviews


def test_returns_only_flagged_reviews(sample_reviews):
    result = flagged_reviews(df=sample_reviews)
    assert "error" not in result
    assert result["total_matches"] == 2  # review_id 1 and 2 are flagged


def test_severity_level_filter_is_a_minimum(sample_reviews):
    result = flagged_reviews(severity_level="medium", df=sample_reviews)
    assert "error" not in result
    # only review_id 1 (high) should pass a "medium" minimum -- review_id 2 is "low"
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


