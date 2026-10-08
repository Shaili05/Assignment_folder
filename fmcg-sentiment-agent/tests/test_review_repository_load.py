import pandas as pd
import pytest

from src.exceptions.exceptions import InvalidRequestError
from src.repositories import review_repository
from src.repositories.review_repository import (
    apply_filters, get_as_of_date, in_window, load_reviews, sentiment_counts, window_bounds,
)

CSV_TEXT = (
    "submission_time,is_safety_issue,aspects,matched_terms,issue_type,severity_level,"
    "product_name,brand_name,review_text,sentiment,rating\n"
    "2023-01-05,False,packaging,,none,none,Test Cream,TestBrand,Nice jar,positive,5\n"
    "2023-01-20,True,,burning,safety,high,Test Cream,,Burned my skin,negative,1\n"
    "2023-02-02,False,price,,none,none,,OtherBrand,Too pricey,neutral,3\n"
)


@pytest.fixture
def csv_path(tmp_path, monkeypatch):
    monkeypatch.setattr(review_repository, "_cache", {})
    path = tmp_path / "reviews.csv"
    path.write_text(CSV_TEXT, encoding="utf-8")
    return path


def test_load_reviews_prepares_the_columns(csv_path):
    frame = load_reviews(csv_path)
    assert list(frame["review_id"]) == [0, 1, 2]
    assert str(frame["submission_time"].dtype).startswith("datetime64")
    assert frame["is_safety_issue"].dtype == bool
    assert frame.loc[1, "aspects"] == ""
    assert frame.loc[2, "product_name"] == ""
    assert frame.loc[1, "brand_name"] == ""


def test_load_reviews_reads_the_file_only_once(csv_path):
    first = load_reviews(csv_path)
    csv_path.unlink()
    assert load_reviews(csv_path) is first


def test_load_reviews_uses_the_environment_path(csv_path, monkeypatch):
    monkeypatch.setenv("REVIEWS_PATH", str(csv_path))
    assert len(load_reviews()) == 3


def test_as_of_date_defaults_to_the_newest_review(csv_path):
    frame = load_reviews(csv_path)
    assert get_as_of_date(frame) == pd.Timestamp("2023-02-02")
    assert get_as_of_date(frame, "2023-01-31") == pd.Timestamp("2023-01-31")


def test_apply_filters_by_aspect_product_and_brand(csv_path):
    frame = load_reviews(csv_path)
    assert list(apply_filters(frame, aspect="price")["review_id"]) == [2]
    assert list(apply_filters(frame, product_name="test cream")["review_id"]) == [0, 1]
    assert list(apply_filters(frame, brand_name="otherbrand")["review_id"]) == [2]
    assert len(apply_filters(frame)) == 3


def test_apply_filters_rejects_an_unknown_aspect(csv_path):
    with pytest.raises(InvalidRequestError):
        apply_filters(load_reviews(csv_path), aspect="colour")


def test_window_bounds_for_the_last_days_and_for_dates():
    as_of = pd.Timestamp("2023-03-21")
    assert window_bounds(as_of, last_n_days=7) == (pd.Timestamp("2023-03-15"), as_of)
    assert window_bounds(as_of, start_date="2023-03-01") == (pd.Timestamp("2023-03-01"), as_of)
    assert window_bounds(as_of) == (None, as_of)


def test_in_window_keeps_the_whole_last_day(csv_path):
    frame = load_reviews(csv_path)
    inside = in_window(frame, pd.Timestamp("2023-01-10"), pd.Timestamp("2023-01-20"))
    assert list(inside["review_id"]) == [1]
    assert len(in_window(frame, None, pd.Timestamp("2023-02-02"))) == 3


def test_sentiment_counts_for_an_empty_selection(csv_path):
    empty = load_reviews(csv_path).iloc[0:0]
    result = sentiment_counts(empty)
    assert result["n_reviews"] == 0
    assert result["pct"] == {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
    assert result["net_sentiment"] == 0.0


