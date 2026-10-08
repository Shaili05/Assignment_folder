from datetime import datetime

import pandas as pd

from src.config.constants import (
    PROFILE_COLUMN_DESCRIPTIONS, PROFILE_DATASET, PROFILE_DERIVED_COLUMNS, PROFILE_EXAMPLE_CHARS,
    PROFILE_EXAMPLE_COUNT, PROFILE_EXCLUDED_COLUMNS, PROFILE_FREQUENCY_LIMIT,
    PROFILE_MAX_DISTINCT_FOR_FREQUENCIES, PROFILE_PROJECT_COLUMNS, PROFILE_SENSITIVE_COLUMNS,
)

from src.exceptions.exceptions import InvalidRequestError, ReviewsNotFoundError
from src.mcp.tools.flagged_reviews import flagged_reviews
from src.mcp.tools.sentiment_trend import sentiment_trend
from src.mcp.tools.summary_report import generate_summary_report
from src.repositories.review_repository import (
    ASPECTS, SEVERITY_LEVELS, load_reviews, sentiment_counts,
)


def check_result(result):
    if "error" in result:
        raise InvalidRequestError(result["error"])
    return result


def get_sentiment_trend(aspect, product_name, brand_name, granularity, periods, as_of):
    return check_result(sentiment_trend(
        aspect=aspect,
        product_name=product_name,
        brand_name=brand_name,
        granularity=granularity,
        periods=periods,
        as_of=as_of,
    ))


def get_flagged_reviews(severity_level, issue_type, last_n_days, start_date, end_date,
                        product_name, brand_name, limit, as_of, full_text=False):
    return check_result(flagged_reviews(
        severity_level=severity_level,
        issue_type=issue_type,
        last_n_days=last_n_days,
        start_date=start_date,
        end_date=end_date,
        product_name=product_name,
        brand_name=brand_name,
        limit=limit,
        as_of=as_of,
        full_text=full_text,
    ))


def get_overview(window_days, as_of, product_name, brand_name):
    return check_result(generate_summary_report(
        window_days=window_days,
        as_of=as_of,
        product_name=product_name,
        brand_name=brand_name,
    ))


def get_all_time_stats():
    frame = load_reviews()
    total = len(frame)
    overall = sentiment_counts(frame)
    flagged = frame[frame["is_safety_issue"]]
    aspects = []
    for aspect in ASPECTS:
        group = frame[frame["aspects"].str.contains(aspect)]
        if group.empty:
            continue
        aspects.append({"aspect": aspect, **sentiment_counts(group)})
    severity_counts = {lvl: int((flagged["severity_level"] == lvl).sum()) for lvl in SEVERITY_LEVELS}
    issue_type_counts = (
        {str(k): int(v) for k, v in flagged.groupby("issue_type").size().to_dict().items()}
        if not flagged.empty else {}
    )
    return {
        "total_reviews": total,
        "overall": overall,
        "flagged_total": int(flagged.shape[0]),
        "start_date": str(frame["submission_time"].min().date()),
        "end_date": str(frame["submission_time"].max().date()),
        "aspects": aspects,
        "severity_counts": severity_counts,
        "issue_type_counts": issue_type_counts,
    }


def get_product_options():
    frame = load_reviews()
    return sorted(n for n in frame["product_name"].dropna().unique() if str(n).strip())


def get_product_span(product_name=None):
    frame = load_reviews()
    if product_name and product_name != "All products":
        frame = frame[frame["product_name"] == product_name]
    if frame.empty:
        raise ReviewsNotFoundError(f"No reviews found for {product_name}")
    return {
        "count": int(len(frame)),
        "first": str(frame["submission_time"].min().date()),
        "last": str(frame["submission_time"].max().date()),
    }

def column_kind(series):
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    if pd.api.types.is_float_dtype(series):
        return "decimal"
    return "text"


def column_source(name):
    if name in PROFILE_DERIVED_COLUMNS:
        return "derived"
    if name in PROFILE_PROJECT_COLUMNS:
        return "project"
    return "kaggle"

def shorten_example(text):
    text = " ".join(str(text).split())
    if len(text) <= PROFILE_EXAMPLE_CHARS:
        return text
    return text[:PROFILE_EXAMPLE_CHARS].rstrip() + "..."


def format_value(value, kind):
    if kind == "date":
        return value.strftime("%d-%b-%Y")
    if kind == "integer":
        return str(int(value))
    if kind == "decimal":
        return f"{value:g}"
    if kind == "boolean":
        return str(bool(value))
    return shorten_example(value)


def column_profile(name, series):
    kind = column_kind(series)
    text = series.astype("string")
    filled = series.notna() & text.str.strip().ne("")
    values = series[filled]
    total = len(series)
    distinct = int(values.nunique())
    entry = {
        "name": name,
        "kind": kind,
        "source": column_source(name),
        "description": PROFILE_COLUMN_DESCRIPTIONS.get(name, ""),
        "null_count": int(total - filled.sum()),
        "percent_populated": round(100 * int(filled.sum()) / total, 2),
        "distinct_count": distinct,
        "minimum": None,
        "maximum": None,
        "max_length": None,
        "examples": [],
        "frequencies": [],
    }
    if kind in ("integer", "decimal", "date") and len(values):
        entry["minimum"] = format_value(values.min(), kind)
        entry["maximum"] = format_value(values.max(), kind)
    if kind == "text" and len(values):
        entry["max_length"] = int(text[filled].str.len().max())
    if name not in PROFILE_SENSITIVE_COLUMNS:
        entry["examples"] = [
            format_value(value, kind) for value in values.drop_duplicates().head(PROFILE_EXAMPLE_COUNT)
        ]
    if kind != "date" and name not in PROFILE_SENSITIVE_COLUMNS and 0 < distinct <= PROFILE_MAX_DISTINCT_FOR_FREQUENCIES:
        counts = values.value_counts().head(PROFILE_FREQUENCY_LIMIT)
        entry["frequencies"] = [
            {"value": str(value), "count": int(count), "percent": round(100 * int(count) / total, 2)}
            for value, count in counts.items()
        ]
    return entry



def get_data_profile():
    frame = load_reviews()
    columns = [
        column_profile(name, frame[name]) for name in frame.columns if name not in PROFILE_EXCLUDED_COLUMNS
    ]
    return {
        "dataset": PROFILE_DATASET["name"],
        "source": PROFILE_DATASET["source"],
        "source_url": PROFILE_DATASET["url"],
        "file": PROFILE_DATASET["file"],
        "row_count": len(frame),
        "column_count": len(columns),
        "generated_at": datetime.now().strftime("%d %b %Y %H:%M"),
        "columns": columns,
    }

