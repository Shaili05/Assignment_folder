"""
make_gold_set.py

Builds the hand-labeling sheet used to measure labeling accuracy.

Sample mix (default 120 reviews):
  70 random, stratified by rating   -> sentiment and aspect accuracy
  30 flagged by the safety rules    -> flag precision
  20 unflagged with rating <= 2     -> missed-issue check (recall)

The template is shuffled and does not show which group a row came from.
The group of each review is written separately to gold_set_meta.csv.

Run:
    python src/data_prep/make_gold_set.py
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

TEMPLATE_COLUMNS = ["review_id", "rating", "product_name", "review_text"]
LABEL_COLUMNS = ["gold_sentiment", "gold_aspects", "gold_issue"]


def stratified_sample(df, n, seed):
    frac = n / len(df)
    parts = [group.sample(frac=frac, random_state=seed) for _, group in df.groupby("rating")]
    sampled = pd.concat(parts)
    if len(sampled) > n:
        sampled = sampled.sample(n=n, random_state=seed)
    elif len(sampled) < n:
        rest = df.drop(sampled.index)
        sampled = pd.concat([sampled, rest.sample(n=n - len(sampled), random_state=seed)])
    return sampled


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/labeled/reviews_scrubbed.csv")
    ap.add_argument("--output-dir", default="data/gold")
    ap.add_argument("--n-random", type=int, default=70)
    ap.add_argument("--n-flagged", type=int, default=30)
    ap.add_argument("--n-missed", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    template_path = out_dir / "gold_set_template.csv"
    meta_path = out_dir / "gold_set_meta.csv"

    if template_path.exists() and not args.force:
        raise SystemExit(f"{template_path} already exists. Use --force to overwrite it.")

    df = pd.read_csv(args.input, low_memory=False)
    df.index.name = "review_id"
    df["is_safety_issue"] = df["is_safety_issue"].astype(bool)

    random_part = stratified_sample(df, args.n_random, args.seed)
    used = set(random_part.index)

    flagged_pool = df[df["is_safety_issue"] & ~df.index.isin(used)]
    flagged_part = flagged_pool.sample(n=min(args.n_flagged, len(flagged_pool)), random_state=args.seed)
    used |= set(flagged_part.index)

    missed_pool = df[~df["is_safety_issue"] & (df["rating"] <= 2) & ~df.index.isin(used)]
    missed_part = missed_pool.sample(n=min(args.n_missed, len(missed_pool)), random_state=args.seed)

    parts = [
        random_part.assign(sample_type="random"),
        flagged_part.assign(sample_type="flagged"),
        missed_part.assign(sample_type="unflagged_low_rating"),
    ]
    gold = pd.concat(parts).sample(frac=1, random_state=args.seed).reset_index()

    out_dir.mkdir(parents=True, exist_ok=True)

    template = gold[TEMPLATE_COLUMNS].copy()
    for col in LABEL_COLUMNS:
        template[col] = ""
    template.to_csv(template_path, index=False, encoding="utf-8-sig")
    gold[["review_id", "sample_type"]].to_csv(meta_path, index=False)

    counts = gold["sample_type"].value_counts().to_dict()
    print(f"Wrote {template_path} ({len(template)} rows)")
    print(f"Wrote {meta_path}")
    print(f"Sample mix: {counts}")

    log_run(
        script_name="make_gold_set.py",
        params=f"input={args.input}, seed={args.seed}, n_random={args.n_random}, n_flagged={args.n_flagged}, n_missed={args.n_missed}",
        summary=f"rows={len(template)}, mix={counts}",
    )


if __name__ == "__main__":
    main()


