"""
data_access.py

Shared loading, date handling and filtering for the review tools.
Set REVIEWS_PATH in the environment to point the tools at another CSV.
"""

import os
from pathlib import Path

import pandas as pd

from src.config.constants import ASPECTS, SENTIMENTS, SEVERITY_LEVELS
from src.config.settings import REVIEWS_PATH as DEFAULT_REVIEWS_PATH

TEXT_COLUMNS = [
    "aspects", "matched_terms", "issue_type", "severity_level",
    "product_name", "brand_name", "review_text", "sentiment",
]

_cache = {}


def load_reviews(path=None):
    path = Path(path or os.environ.get("REVIEWS_PATH", DEFAULT_REVIEWS_PATH))
    key = str(path)
    if key not in _cache:
        df = pd.read_csv(path, low_memory=False)
        df["review_id"] = df.index
        df["submission_time"] = pd.to_datetime(df["submission_time"], errors="coerce")
        df["is_safety_issue"] = df["is_safety_issue"].astype(bool)
        for col in TEXT_COLUMNS:
            df[col] = df[col].fillna("").astype(str)
        _cache[key] = df
    return _cache[key]


def get_as_of_date(df, as_of=None):
    if as_of:
        return pd.Timestamp(as_of).normalize()
    return df["submission_time"].max().normalize()


def apply_filters(df, aspect=None, product_name=None, brand_name=None):
    data = df
    if aspect:
        if aspect not in ASPECTS:
            raise ValueError(f"Unknown aspect '{aspect}'. Valid aspects: {', '.join(ASPECTS)}")
        data = data[data["aspects"].str.contains(aspect)]
    if product_name:
        data = data[data["product_name"].str.contains(product_name, case=False, regex=False)]
    if brand_name:
        data = data[data["brand_name"].str.contains(brand_name, case=False, regex=False)]
    return data


def window_bounds(as_of_date, last_n_days=None, start_date=None, end_date=None):
    if last_n_days:
        end = as_of_date
        start = as_of_date - pd.Timedelta(days=int(last_n_days) - 1)
        return start, end
    start = pd.Timestamp(start_date).normalize() if start_date else None
    end = pd.Timestamp(end_date).normalize() if end_date else as_of_date
    return start, end


def in_window(df, start, end):
    mask = df["submission_time"] <= end + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    if start is not None:
        mask &= df["submission_time"] >= start
    return df[mask]


def sentiment_counts(data):
    total = len(data)
    counts = {s: int((data["sentiment"] == s).sum()) for s in SENTIMENTS}
    pct = {s: round(100 * counts[s] / total, 1) if total else 0.0 for s in SENTIMENTS}
    return {
        "n_reviews": total,
        "counts": counts,
        "pct": pct,
        "net_sentiment": round(pct["positive"] - pct["negative"], 1),
    }


