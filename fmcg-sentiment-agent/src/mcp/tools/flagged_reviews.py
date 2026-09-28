"""
flagged_reviews.py


Tool 2: reviews flagged for a safety or quality issue, sorted by severity.
severity_level acts as a minimum: "medium" returns medium and high.


Run:
    python -m src.mcp.tools.flagged_reviews --level high --days 365
"""


import argparse
import json

from src.data_prep.safety_flags import first_match_position
from src.repositories.review_repository import (
    SEVERITY_LEVELS, apply_filters, get_as_of_date, in_window, load_reviews, window_bounds,
)

ISSUE_TYPES = ["safety", "quality", "both"]
EXCERPT_CHARS = 400


def issue_excerpt(text):
    position = first_match_position(text)
    if position is None or len(text) <= EXCERPT_CHARS:
        return text[:EXCERPT_CHARS]
    start = max(0, position - 150)
    end = min(len(text), start + EXCERPT_CHARS)
    return ("..." if start > 0 else "") + text[start:end] + ("..." if end < len(text) else "")


def flagged_reviews(severity_level=None, issue_type=None, last_n_days=None, start_date=None,
                    end_date=None, product_name=None, brand_name=None, limit=10, as_of=None,
                    full_text=False, df=None):
    try:
        if severity_level and severity_level not in SEVERITY_LEVELS:
            raise ValueError(f"severity_level must be one of: {', '.join(SEVERITY_LEVELS)}")
        if issue_type and issue_type not in ISSUE_TYPES:
            raise ValueError(f"issue_type must be one of: {', '.join(ISSUE_TYPES)}")
        limit = max(1, min(int(limit), 50))

        df = load_reviews() if df is None else df
        as_of_date = get_as_of_date(df, as_of)
        start, end = window_bounds(as_of_date, last_n_days, start_date, end_date)
        data = apply_filters(df, None, product_name, brand_name)
        data = in_window(data[data["submission_time"].notna()], start, end)
    except ValueError as exc:
        return {"error": str(exc)}

    data = data[data["is_safety_issue"]]
    if severity_level:
        allowed = SEVERITY_LEVELS[SEVERITY_LEVELS.index(severity_level):]
        data = data[data["severity_level"].isin(allowed)]
    if issue_type:
        data = data[data["issue_type"] == issue_type]

    data = data.sort_values(["severity_score", "submission_time"], ascending=[False, False])

    reviews = []
    for _, row in data.head(limit).iterrows():
        reviews.append({
            "review_id": int(row["review_id"]),
            "submission_time": str(row["submission_time"].date()),
            "rating": int(row["rating"]),
            "product_name": row["product_name"],
            "brand_name": row["brand_name"],
            "issue_type": row["issue_type"],
            "severity_score": float(row["severity_score"]),
            "severity_level": row["severity_level"],
            "matched_terms": [t for t in row["matched_terms"].split("|") if t],
            "review_text": row["review_text"] if full_text else issue_excerpt(row["review_text"]),
        })

    return {
        "tool": "flagged_reviews",
        "window": {
            "start": str(start.date()) if start is not None else None,
            "end": str(end.date()),
            "as_of_date": str(as_of_date.date()),
        },
        "total_matches": int(len(data)),
        "returned": len(reviews),
        "counts_by_level": {lvl: int((data["severity_level"] == lvl).sum()) for lvl in SEVERITY_LEVELS},
        "counts_by_issue_type": {t: int((data["issue_type"] == t).sum()) for t in ISSUE_TYPES},
        "reviews": reviews,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default=None)
    ap.add_argument("--issue-type", default=None)
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()

    result = flagged_reviews(args.level, args.issue_type, args.days, limit=args.limit)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
