import logging
import shutil
from pathlib import Path


import pandas as pd


from src.config.settings import LABELED_REVIEWS_PATH, REVIEWS_PATH, VECTORSTORE_DIR
from src.data_prep.label_rules import rating_to_sentiment, rule_aspects
from src.config.constants import ASPECTS
from src.data_prep.recompute_safety_flags import FLAG_COLUMNS, sync_chroma
from src.data_prep.safety_flags import analyze_review
from src.utils.output import write_line
from src.utils.run_log import log_run


logger = logging.getLogger(__name__)


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
        df, old_sentiment, old_flagged = apply_rules(path)
        write_line(f"{path.name}")
        write_line(f"  sentiment before: {old_sentiment}")
        write_line(f"  sentiment after:  {df['sentiment'].value_counts().to_dict()}")
        write_line(f"  flagged: {old_flagged} -> {int(df['is_safety_issue'].sum())}")
        if name == scrubbed:
            scrubbed_df = df


    if scrubbed_df is None:
        raise SystemExit("Scrubbed CSV not found, nothing to sync.")

    counts = {a: int(scrubbed_df["aspects"].str.contains(a).sum()) for a in ASPECTS}
    write_line(f"Aspect counts: {counts}")


    if skip_chroma:
        write_line("Chroma sync skipped")
    else:
        write_line(f"Syncing metadata to {chroma_dir}")
        sync_chroma(scrubbed_df, chroma_dir, collection)


    log_run(
        script_name="apply_label_rules.py",
        params=f"scrubbed={scrubbed}, labeled={labeled}, skip_chroma={skip_chroma}",
        summary=f"sentiment={scrubbed_df['sentiment'].value_counts().to_dict()}, aspects={counts}",
    )
