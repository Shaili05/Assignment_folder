"""
review_service.py


Business logic between the routers and the review tools. Tool errors and
missing data are raised as domain exceptions; exception handlers turn them
into HTTP responses.
"""

from src.exceptions.exceptions import InvalidRequestError, ReviewsNotFoundError
from src.mcp.tools.flagged_reviews import flagged_reviews
from src.mcp.tools.sentiment_trend import sentiment_trend
from src.mcp.tools.summary_report import generate_summary_report
from src.repositories.review_repository import (
    ASPECTS, SEVERITY_LEVELS, get_as_of_date, load_reviews, sentiment_counts,
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


def get_data_as_of():
    frame = load_reviews()
    return str(get_as_of_date(frame).date())
