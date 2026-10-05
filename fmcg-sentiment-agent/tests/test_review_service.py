import pytest

from src.config.constants import ASPECTS, SEVERITY_LEVELS
from src.exceptions.exceptions import InvalidRequestError, ReviewsNotFoundError
from src.services import review_service


@pytest.fixture
def reviews(monkeypatch, sample_reviews):
    monkeypatch.setattr(review_service, "load_reviews", lambda: sample_reviews)
    return sample_reviews


def test_trend_passes_every_argument_to_the_tool(monkeypatch):
    seen = {}

    def fake_tool(**kwargs):
        seen.update(kwargs)
        return {"tool": "sentiment_trend"}

    monkeypatch.setattr(review_service, "sentiment_trend", fake_tool)
    result = review_service.get_sentiment_trend("price", "Test Cleanser", "TestBrand", "month", 6, "2023-02-01")
    assert result == {"tool": "sentiment_trend"}
    assert seen == {
        "aspect": "price", "product_name": "Test Cleanser", "brand_name": "TestBrand",
        "granularity": "month", "periods": 6, "as_of": "2023-02-01",
    }


def test_trend_error_becomes_an_invalid_request(monkeypatch):
    monkeypatch.setattr(review_service, "sentiment_trend", lambda **kwargs: {"error": "bad granularity"})
    with pytest.raises(InvalidRequestError):
        review_service.get_sentiment_trend(None, None, None, "day", 6, None)


def test_flagged_reviews_pass_every_argument_to_the_tool(monkeypatch):
    seen = {}

    def fake_tool(**kwargs):
        seen.update(kwargs)
        return {"tool": "flagged_reviews"}

    monkeypatch.setattr(review_service, "flagged_reviews", fake_tool)
    review_service.get_flagged_reviews("high", "safety", 30, None, None, None, None, 10, None, full_text=True)
    assert seen["severity_level"] == "high"
    assert seen["issue_type"] == "safety"
    assert seen["last_n_days"] == 30
    assert seen["limit"] == 10
    assert seen["full_text"] is True


def test_flagged_reviews_error_becomes_an_invalid_request(monkeypatch):
    monkeypatch.setattr(review_service, "flagged_reviews", lambda **kwargs: {"error": "bad level"})
    with pytest.raises(InvalidRequestError):
        review_service.get_flagged_reviews("extreme", None, None, None, None, None, None, 10, None)


def test_overview_passes_every_argument_to_the_report(monkeypatch):
    seen = {}

    def fake_report(**kwargs):
        seen.update(kwargs)
        return {"tool": "generate_summary_report"}

    monkeypatch.setattr(review_service, "generate_summary_report", fake_report)
    result = review_service.get_overview(14, "2023-02-01", "Test Cleanser", None)
    assert result == {"tool": "generate_summary_report"}
    assert seen == {"window_days": 14, "as_of": "2023-02-01", "product_name": "Test Cleanser", "brand_name": None}


def test_overview_error_becomes_an_invalid_request(monkeypatch):
    monkeypatch.setattr(review_service, "generate_summary_report", lambda **kwargs: {"error": "bad window"})
    with pytest.raises(InvalidRequestError):
        review_service.get_overview(0, None, None, None)


def test_all_time_stats_count_reviews_flags_and_dates(reviews):
    stats = review_service.get_all_time_stats()
    assert stats["total_reviews"] == 5
    assert stats["flagged_total"] == 2
    assert stats["start_date"] == "2023-01-05"
    assert stats["end_date"] == "2023-02-10"
    assert stats["overall"]["counts"] == {"positive": 2, "neutral": 1, "negative": 2}
    assert stats["issue_type_counts"] == {"quality": 1, "safety": 1}
    assert list(stats["severity_counts"]) == SEVERITY_LEVELS
    assert stats["severity_counts"] == {"low": 1, "medium": 0, "high": 1}


def test_all_time_stats_skip_aspects_without_reviews(reviews):
    stats = review_service.get_all_time_stats()
    names = [entry["aspect"] for entry in stats["aspects"]]
    assert names == [aspect for aspect in ASPECTS if aspect != "availability"]
    packaging = next(entry for entry in stats["aspects"] if entry["aspect"] == "packaging")
    assert packaging["n_reviews"] == 2


def test_all_time_stats_without_flagged_reviews(monkeypatch, sample_reviews):
    calm = sample_reviews[~sample_reviews["is_safety_issue"]].reset_index(drop=True)
    monkeypatch.setattr(review_service, "load_reviews", lambda: calm)
    stats = review_service.get_all_time_stats()
    assert stats["flagged_total"] == 0
    assert stats["issue_type_counts"] == {}
    assert stats["severity_counts"] == {"low": 0, "medium": 0, "high": 0}


def test_product_options_are_sorted_and_unique(reviews):
    assert review_service.get_product_options() == ["Test Cleanser", "Test Moisturizer"]


def test_product_span_for_all_products(reviews):
    assert review_service.get_product_span() == {"count": 5, "first": "2023-01-05", "last": "2023-02-10"}
    assert review_service.get_product_span("All products")["count"] == 5


def test_product_span_for_one_product(reviews):
    assert review_service.get_product_span("Test Cleanser") == {
        "count": 2, "first": "2023-01-15", "last": "2023-02-01",
    }


def test_product_span_for_an_unknown_product_raises(reviews):
    with pytest.raises(ReviewsNotFoundError):
        review_service.get_product_span("Nothing Cream")


