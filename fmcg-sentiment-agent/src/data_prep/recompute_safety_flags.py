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

import logging
import shutil
from pathlib import Path


import pandas as pd


from src.config.settings import LABELED_REVIEWS_PATH, REVIEWS_PATH, VECTORSTORE_DIR
from src.data_prep.safety_flags import analyze_review
from src.utils.output import write_line
from src.utils.run_log import log_run


logger = logging.getLogger(__name__)


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
        logger.info("Updated %d / %d vectors", end, len(df))


def run(labeled=None, scrubbed=None, chroma_dir=None, collection="reviews", skip_chroma=False):
    labeled = labeled or str(LABELED_REVIEWS_PATH)
    scrubbed = scrubbed or str(REVIEWS_PATH)
    chroma_dir = chroma_dir or str(VECTORSTORE_DIR)


    scrubbed_df = None
    for name in [labeled, scrubbed]:
        path = Path(name)
        if not path.exists():
            logger.warning("Skipped %s (file not found)", name)
            continue
        df, old_flagged = recompute_file(path)
        write_line(f"{path.name}: flagged {old_flagged} -> {int(df['is_safety_issue'].sum())} of {len(df)} rows")
        if name == scrubbed:
            scrubbed_df = df


    if scrubbed_df is None:
        raise SystemExit("Scrubbed CSV not found, nothing to sync.")


    flagged = scrubbed_df[scrubbed_df["is_safety_issue"]]
    write_line(f"Issue types: {flagged['issue_type'].value_counts().to_dict()}")
    write_line(f"Severity levels: {flagged['severity_level'].value_counts().to_dict()}")


    if skip_chroma:
        write_line("Chroma sync skipped")
    else:
        write_line(f"Syncing metadata to {chroma_dir}")
        sync_chroma(scrubbed_df, chroma_dir, collection)


    log_run(
        script_name="recompute_safety_flags.py",
        params=f"scrubbed={scrubbed}, labeled={labeled}, chroma_dir={chroma_dir}, skip_chroma={skip_chroma}",
        summary=f"flagged={len(flagged)}, issue_types={flagged['issue_type'].value_counts().to_dict()}",
    )

