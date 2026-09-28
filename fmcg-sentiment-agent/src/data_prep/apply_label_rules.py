"""
apply_label_rules.py

Replaces the sentiment and aspect labels in the labeled and scrubbed CSVs with
the rule-based labels from label_rules.py, recomputes the safety/quality flags
with the new sentiment, and syncs the Chroma metadata. No re-embedding needed.

The previous files are kept once as *_before_label_fix.csv.

Run:
    python src/data_prep/apply_label_rules.py
"""

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

from label_rules import ASPECT_ORDER, rating_to_sentiment, rule_aspects
from recompute_safety_flags import FLAG_COLUMNS, sync_chroma
from safety_flags import analyze_review


def apply_rules(path):
    df = pd.read_csv(path, low_memory=False)
    old_sentiment = df["sentiment"].value_counts().to_dict()
    old_flagged = int(df["is_safety_issue"].astype(bool).sum())

    backup_path = path.with_name(path.stem + "_before_label_fix.csv")
    if not backup_path.exists():
        shutil.copy(path, backup_path)

    df["sentiment"] = df["rating"].map(rating_to_sentiment)
    df["aspects"] = df["review_text"].map(rule_aspects)
    if "sentiment_confidence" in df.columns:
        df = df.drop(columns=["sentiment_confidence"])

    flags = pd.DataFrame(
        [analyze_review(t, s, r) for t, s, r in zip(df["review_text"], df["sentiment"], df["rating"])],
        index=df.index,
    )
    for col in FLAG_COLUMNS:
        df[col] = flags[col]

    df.to_csv(path, index=False)
    return df, old_sentiment, old_flagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scrubbed", default="data/labeled/reviews_scrubbed.csv")
    ap.add_argument("--labeled", default="data/labeled/labeled_reviews.csv")
    ap.add_argument("--chroma-dir", default="data/vectorstore/chroma_db")
    ap.add_argument("--collection", default="reviews")
    ap.add_argument("--skip-chroma", action="store_true")
    args = ap.parse_args()

    scrubbed_df = None
    for name in [args.labeled, args.scrubbed]:
        path = Path(name)
        if not path.exists():
            print(f"Skipped {name} (file not found)")
            continue
        df, old_sentiment, old_flagged = apply_rules(path)
        print(f"{path.name}")
        print(f"  sentiment before: {old_sentiment}")
        print(f"  sentiment after:  {df['sentiment'].value_counts().to_dict()}")
        print(f"  flagged: {old_flagged} -> {int(df['is_safety_issue'].sum())}")
        if name == args.scrubbed:
            scrubbed_df = df

    if scrubbed_df is None:
        raise SystemExit("Scrubbed CSV not found, nothing to sync.")

    counts = {a: int(scrubbed_df["aspects"].str.contains(a).sum()) for a in ASPECT_ORDER}
    print(f"Aspect counts: {counts}")

    if args.skip_chroma:
        print("Chroma sync skipped")
    else:
        print(f"Syncing metadata to {args.chroma_dir}")
        sync_chroma(scrubbed_df, args.chroma_dir, args.collection)

    log_run(
        script_name="apply_label_rules.py",
        params=f"scrubbed={args.scrubbed}, labeled={args.labeled}, skip_chroma={args.skip_chroma}",
        summary=f"sentiment={scrubbed_df['sentiment'].value_counts().to_dict()}, aspects={counts}",
    )


if __name__ == "__main__":
    main()


