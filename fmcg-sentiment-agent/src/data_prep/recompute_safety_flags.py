"""
recompute_safety_flags.py

Recomputes the safety/quality flag columns with safety_flags.analyze_review
in the labeled and scrubbed CSVs, then syncs the metadata of the production
Chroma collection. Embeddings are not touched, so no re-embedding is needed.

New columns: issue_type, severity_level, matched_terms.
Updated columns: is_safety_issue, severity_score.
Extra Chroma metadata: submission_ts (YYYYMMDD integer) and product_id.

Run:
    python src/data_prep/recompute_safety_flags.py
"""

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

from safety_flags import analyze_review

FLAG_COLUMNS = ["is_safety_issue", "issue_type", "severity_score", "severity_level", "matched_terms"]

TEXT_METADATA = [
    "aspects", "sentiment", "product_id", "product_name", "brand_name",
    "user_id", "issue_type", "severity_level", "matched_terms",
]

BATCH_SIZE = 500


def recompute_file(path):
    df = pd.read_csv(path, low_memory=False)
    old_flagged = int(df["is_safety_issue"].astype(bool).sum()) if "is_safety_issue" in df.columns else 0

    backup_path = path.with_name(path.stem + "_before_flag_fix.csv")
    if not backup_path.exists():
        shutil.copy(path, backup_path)

    results = [
        analyze_review(text, sentiment, rating)
        for text, sentiment, rating in zip(df["review_text"], df["sentiment"], df["rating"])
    ]
    result_df = pd.DataFrame(results, index=df.index)
    for col in FLAG_COLUMNS:
        df[col] = result_df[col]

    df.to_csv(path, index=False)
    return df, old_flagged


def build_metadata(df):
    dates = pd.to_datetime(df["submission_time"], errors="coerce").dt.strftime("%Y%m%d")
    dates = pd.to_numeric(dates, errors="coerce").fillna(0).astype(int)

    records = []
    for i in range(len(df)):
        row = df.iloc[i]
        record = {
            "rating": int(row["rating"]),
            "is_safety_issue": bool(row["is_safety_issue"]),
            "severity_score": float(row["severity_score"]),
            "submission_ts": int(dates.iloc[i]),
        }
        for col in TEXT_METADATA:
            value = row[col]
            record[col] = "" if pd.isna(value) else str(value)
        records.append(record)
    return records


def sync_chroma(df, chroma_dir, collection_name):
    import chromadb

    client = chromadb.PersistentClient(path=chroma_dir)
    collection = client.get_collection(collection_name)

    if collection.count() != len(df):
        raise SystemExit(
            f"Row mismatch: collection has {collection.count()} vectors, CSV has {len(df)} rows."
        )

    ids = [str(i) for i in df.index]
    metadatas = build_metadata(df)

    for start in range(0, len(df), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(df))
        collection.update(ids=ids[start:end], metadatas=metadatas[start:end])
        print(f"  Updated {end} / {len(df)} vectors")


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
        df, old_flagged = recompute_file(path)
        print(f"{path.name}: flagged {old_flagged} -> {int(df['is_safety_issue'].sum())} of {len(df)} rows")
        if name == args.scrubbed:
            scrubbed_df = df

    if scrubbed_df is None:
        raise SystemExit("Scrubbed CSV not found, nothing to sync.")

    flagged = scrubbed_df[scrubbed_df["is_safety_issue"]]
    print(f"Issue types: {flagged['issue_type'].value_counts().to_dict()}")
    print(f"Severity levels: {flagged['severity_level'].value_counts().to_dict()}")

    if args.skip_chroma:
        print("Chroma sync skipped")
    else:
        print(f"Syncing metadata to {args.chroma_dir}")
        sync_chroma(scrubbed_df, args.chroma_dir, args.collection)

    log_run(
        script_name="recompute_safety_flags.py",
        params=f"scrubbed={args.scrubbed}, labeled={args.labeled}, chroma_dir={args.chroma_dir}, skip_chroma={args.skip_chroma}",
        summary=f"flagged={len(flagged)}, issue_types={flagged['issue_type'].value_counts().to_dict()}",
    )


if __name__ == "__main__":
    main()


