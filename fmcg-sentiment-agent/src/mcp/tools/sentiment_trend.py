"""
sentiment_trend.py

Tool 1: sentiment counts and shares over time, optionally for one aspect,
product or brand. Periods are calendar weeks or months, counted back from the
newest review in the data.

Run:
    python -m src.mcp.tools.sentiment_trend --aspect packaging --granularity month --periods 6
"""

import logging

import pandas as pd

from src.repositories.review_repository import apply_filters, get_as_of_date, load_reviews, sentiment_counts

logger = logging.getLogger(__name__)

FREQ = {"week": "W", "month": "M", "year": "Y"}
LOW_SAMPLE = 10


def period_label(period, granularity):
    if granularity == "week":
        return period.start_time.strftime("%Y-%m-%d")
    return period.strftime("%Y-%m")


def sentiment_trend(aspect=None, product_name=None, brand_name=None, granularity="month",
                    periods=6, as_of=None, df=None):
    try:
        if granularity not in FREQ:
            raise ValueError("granularity must be 'week' or 'month'")
        periods = int(periods)
        if periods < 1 or periods > 60:
            raise ValueError("periods must be between 1 and 60")

        df = load_reviews() if df is None else df
        as_of_date = get_as_of_date(df, as_of)
        data = apply_filters(df, aspect, product_name, brand_name)
        data = data[data["submission_time"].notna() & (data["submission_time"] <= as_of_date + pd.Timedelta(days=1))]
    except ValueError as exc:
        logger.warning("sentiment_trend rejected the request: %s", exc)
        return {"error": str(exc)}

    freq = FREQ[granularity]
    end_period = pd.Period(as_of_date, freq=freq)
    all_periods = [end_period - i for i in range(periods - 1, -1, -1)]
    data_periods = data["submission_time"].dt.to_period(freq)

    series = []
    for period in all_periods:
        stats = sentiment_counts(data[data_periods == period])
        series.append({"period": period_label(period, granularity), **stats})

    in_range = data[data_periods.isin(all_periods)]
    notes = []
    notes.append(f"Data ends on {as_of_date.date()}, so the latest period may be partial.")
    if aspect == "texture_effectiveness":
        notes.append("Almost every review mentions texture or effectiveness, so this equals overall sentiment.")
    low = [row["period"] for row in series if 0 < row["n_reviews"] < LOW_SAMPLE]
    if low:
        notes.append(f"Fewer than {LOW_SAMPLE} reviews in: {', '.join(low)}. Treat those shares as noisy.")
    empty = [row["period"] for row in series if row["n_reviews"] == 0]
    if empty:
        notes.append(f"No reviews in: {', '.join(empty)}.")

    change = None
    latest, previous = series[-1], series[-2] if len(series) > 1 else None
    if previous and latest["n_reviews"] and previous["n_reviews"]:
        change = {
            "from_period": previous["period"],
            "to_period": latest["period"],
            "negative_pct_change": round(latest["pct"]["negative"] - previous["pct"]["negative"], 1),
            "positive_pct_change": round(latest["pct"]["positive"] - previous["pct"]["positive"], 1),
            "net_sentiment_change": round(latest["net_sentiment"] - previous["net_sentiment"], 1),
        }

    return {
        "tool": "sentiment_trend",
        "filters": {"aspect": aspect, "product_name": product_name, "brand_name": brand_name},
        "granularity": granularity,
        "as_of_date": str(as_of_date.date()),
        "series": series,
        "overall": sentiment_counts(in_range),
        "latest_vs_previous": change,
        "notes": notes,
    }
