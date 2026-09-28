"""
test_sentiment_trend.py

Tests for src/mcp/tools/sentiment_trend.py using an in-memory sample
DataFrame instead of the real CSV.
"""

from src.mcp.tools.sentiment_trend import sentiment_trend


def test_basic_trend_returns_series(sample_reviews):
    result = sentiment_trend(granularity="month", periods=2, df=sample_reviews)
    assert "error" not in result
    assert result["tool"] == "sentiment_trend"
    assert len(result["series"]) == 2


def test_invalid_granularity_returns_error(sample_reviews):
    result = sentiment_trend(granularity="decade", df=sample_reviews)
    assert "error" in result


def test_invalid_aspect_filter_returns_error(sample_reviews):
    result = sentiment_trend(aspect="not_a_real_aspect", df=sample_reviews)
    assert "error" in result


def test_periods_out_of_range_returns_error(sample_reviews):
    result = sentiment_trend(periods=0, df=sample_reviews)
    assert "error" in result
    result = sentiment_trend(periods=100, df=sample_reviews)
    assert "error" in result


def test_product_filter_narrows_results(sample_reviews):
    result = sentiment_trend(product_name="Test Cleanser", granularity="month", periods=2, df=sample_reviews)
    assert "error" not in result
    assert result["overall"]["n_reviews"] == 2  # only the 2 "Test Cleanser" rows


