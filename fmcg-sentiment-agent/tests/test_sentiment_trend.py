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
    assert result["overall"]["n_reviews"] == 2


def test_weekly_periods_are_labelled_with_a_date(sample_reviews):
    result = sentiment_trend(granularity="week", periods=3, df=sample_reviews)
    assert len(result["series"]) == 3
    assert all(len(row["period"]) == 10 for row in result["series"])


def test_texture_note_explains_it_equals_overall_sentiment(sample_reviews):
    result = sentiment_trend(aspect="texture_effectiveness", periods=2, df=sample_reviews)
    assert any("equals overall sentiment" in note for note in result["notes"])


def test_empty_periods_are_named_in_the_notes(sample_reviews):
    result = sentiment_trend(granularity="month", periods=6, df=sample_reviews)
    assert any(note.startswith("No reviews in:") for note in result["notes"])


