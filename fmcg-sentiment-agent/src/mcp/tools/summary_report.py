"""
summary_report.py

Tool 3: brand-health summary for a recent window (default 7 days) compared
with the window before it. Returns the numbers and a ready-to-read markdown
report.

Run:
    python -m src.mcp.tools.summary_report --days 30 --save
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from src.config.constants import ASPECTS, LOW_SAMPLE_THRESHOLD, MIN_PRODUCT_REVIEWS_FOR_TABLE
from src.config.settings import REPORTS_DIR
from src.repositories.review_repository import (
    apply_filters, get_as_of_date, in_window, load_reviews, sentiment_counts, window_bounds,
)
from src.mcp.tools.flagged_reviews import flagged_reviews


def compare(current, previous):
    if not current["n_reviews"] or not previous["n_reviews"]:
        return None
    return {
        "negative_pct_change": round(current["pct"]["negative"] - previous["pct"]["negative"], 1),
        "positive_pct_change": round(current["pct"]["positive"] - previous["pct"]["positive"], 1),
        "net_sentiment_change": round(current["net_sentiment"] - previous["net_sentiment"], 1),
    }


def aspect_table(current, previous):
    rows = []
    for aspect in ASPECTS:
        cur = sentiment_counts(current[current["aspects"].str.contains(aspect)])
        prev = sentiment_counts(previous[previous["aspects"].str.contains(aspect)])
        rows.append({"aspect": aspect, "current": cur, "previous": prev, "change": compare(cur, prev)})
    return rows


def product_table(current, limit=5):
    rows = []
    for name, group in current.groupby("product_name"):
        if len(group) < MIN_PRODUCT_REVIEWS_FOR_TABLE or not name:
            continue
        stats = sentiment_counts(group)
        rows.append({"product_name": name, **stats})
    rows.sort(key=lambda r: (-r["pct"]["negative"], -r["n_reviews"]))
    return rows[:limit]


def signed(value):
    return "n/a" if value is None else f"{value:+.1f}"


def render_markdown(report):
    win, cur, prev = report["window"], report["overall"], report["previous_overall"]
    lines = [
        "# Brand Health Report",
        "",
        f"Period: {win['start']} to {win['end']} ({win['days']} days). Compared with {win['previous_start']} to {win['previous_end']}.",
        "",
        "## Summary",
        "",
        f"- Reviews in period: {cur['n_reviews']} (previous period: {prev['n_reviews']})",
        f"- Positive {cur['pct']['positive']}%, neutral {cur['pct']['neutral']}%, negative {cur['pct']['negative']}%",
        f"- Net sentiment {cur['net_sentiment']:+.1f} (change vs previous: {signed((report['change'] or {}).get('net_sentiment_change'))})",
        f"- Flagged safety or quality reviews: {report['flagged']['total_matches']}",
        "",
        "## Sentiment by aspect",
        "",
        "| Aspect | Reviews | Positive % | Negative % | Net | Change in net |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["aspects"]:
        c = row["current"]
        if c["n_reviews"]:
            cells = [c["pct"]["positive"], c["pct"]["negative"], f"{c['net_sentiment']:+.1f}"]
        else:
            cells = ["-", "-", "-"]
        lines.append(
            f"| {row['aspect']} | {c['n_reviews']} | {cells[0]} | {cells[1]} | "
            f"{cells[2]} | {signed((row['change'] or {}).get('net_sentiment_change'))} |"
        )

    lines += ["", "## Flagged reviews", ""]
    if report["flagged"]["reviews"]:
        for r in report["flagged"]["reviews"]:
            excerpt = r["review_text"][:220].replace("\n", " ")
            lines.append(
                f"- Review {r['review_id']} ({r['submission_time']}, {r['rating']} stars, {r['issue_type']}, "
                f"severity {r['severity_level']} {r['severity_score']}): {excerpt}"
            )
    else:
        lines.append("No flagged reviews in this period.")

    lines += ["", "## Products with the highest negative share", ""]
    if report["products"]:
        lines += ["| Product | Reviews | Negative % | Net |", "|---|---|---|---|"]
        for r in report["products"]:
            lines.append(f"| {r['product_name']} | {r['n_reviews']} | {r['pct']['negative']} | {r['net_sentiment']:+.1f} |")
    else:
        lines.append(f"No product has at least {MIN_PRODUCT_REVIEWS_FOR_TABLE} reviews in this period.")

    lines += ["", "## Notes", ""]
    lines += [f"- {note}" for note in report["notes"]]
    return "\n".join(lines) + "\n"


def generate_summary_report(window_days=7, as_of=None, product_name=None, brand_name=None, df=None):
    try:
        window_days = int(window_days)
        if window_days < 1 or window_days > 3650:
            raise ValueError("window_days must be between 1 and 3650")

        df = load_reviews() if df is None else df
        as_of_date = get_as_of_date(df, as_of)
        data = apply_filters(df, None, product_name, brand_name)
        data = data[data["submission_time"].notna()]
    except ValueError as exc:
        return {"error": str(exc)}

    start, end = window_bounds(as_of_date, window_days)
    prev_end = start - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=window_days - 1)

    current = in_window(data, start, end)
    previous = in_window(data, prev_start, prev_end)
    overall = sentiment_counts(current)
    previous_overall = sentiment_counts(previous)

    flagged = flagged_reviews(last_n_days=window_days, product_name=product_name, brand_name=brand_name,
                              limit=5, as_of=str(as_of_date.date()), df=df)

    notes = [f"Data ends on {as_of_date.date()}; the period is counted back from that date."]
    if overall["n_reviews"] < LOW_SAMPLE_THRESHOLD:
        notes.append(f"Only {overall['n_reviews']} reviews in this period, so percentages are noisy.")
    if previous_overall["n_reviews"] < LOW_SAMPLE_THRESHOLD:
        notes.append(f"Only {previous_overall['n_reviews']} reviews in the previous period, so changes are unreliable.")
    notes.append("texture_effectiveness covers almost every review and mirrors overall sentiment.")
    notes.append("Sentiment follows the star rating; aspects and flags come from keyword rules.")

    report = {
        "tool": "summary_report",
        "window": {
            "days": window_days,
            "start": str(start.date()),
            "end": str(end.date()),
            "previous_start": str(prev_start.date()),
            "previous_end": str(prev_end.date()),
            "as_of_date": str(as_of_date.date()),
        },
        "filters": {"product_name": product_name, "brand_name": brand_name},
        "overall": overall,
        "previous_overall": previous_overall,
        "change": compare(overall, previous_overall),
        "aspects": aspect_table(current, previous),
        "flagged": flagged,
        "products": product_table(current),
        "notes": notes,
    }
    report["markdown"] = render_markdown(report)
    return report


def save_report(report, output_dir=None):
    out_dir = Path(output_dir or REPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    win = report["window"]
    path = out_dir / f"brand_health_report_{win['end']}_{win['days']}d.md"
    path.write_text(report["markdown"], encoding="utf-8")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--product", default=None)
    ap.add_argument("--brand", default=None)
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = generate_summary_report(args.days, args.as_of, args.product, args.brand)
    if "error" in report:
        raise SystemExit(report["error"])

    if args.json:
        print(json.dumps({k: v for k, v in report.items() if k != "markdown"}, indent=2))
    else:
        print(report["markdown"])
    if args.save:
        print(f"Saved {save_report(report)}")


if __name__ == "__main__":
    main()

