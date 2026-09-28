import pandas as pd
import os
import re
from transformers import pipeline

RAW_PATH = "data/raw/raw_reviews.csv"
LABELED_PATH = "data/labeled/labeled_reviews.csv"
CHECKPOINT_PATH = "data/labeled/labeled_reviews_checkpoint.csv"
CHECKPOINT_EVERY = 200

ASPECT_LABELS = ["packaging", "price", "texture_effectiveness", "availability"]
ASPECT_SCORE_THRESHOLD = 0.5

SAFETY_KEYWORDS = [
    "allerg", "rash", "burn", "blister", "swell", "hospital", "reaction",
    "itch", "hive", "infection", "bleeding", "scar", "toxic", "poison",
    "contaminat", "expired", "recall", "chemical smell", "burning sensation",
]


def build_keyword_pattern(keyword):
    """Word-boundary regex so short keywords like 'scar' don't match inside
    unrelated words (e.g. 'mascara')."""
    return re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)


SAFETY_PATTERNS = [build_keyword_pattern(kw) for kw in SAFETY_KEYWORDS]


def get_sentiment_pipeline():
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


def get_aspect_pipeline():
    """
    Zero-shot classification replaces keyword matching for aspects.
    Keyword matching (the previous approach) only fires on exact word
    matches - "break out" (two words) doesn't match a "breakout" keyword,
    "clog the pores" doesn't match anything at all - so any phrasing the
    keyword list didn't anticipate falls through to "general". This model
    reads the review's meaning instead of scanning for exact substrings,
    so it still classifies a review correctly even with wording the
    keyword list never covered.
    """
    return pipeline("zero-shot-classification", model="cross-encoder/nli-distilroberta-base")


def label_sentiment(text, sentiment_pipeline):
    if not isinstance(text, str) or text.strip() == "":
        return "neutral", 0.0
    result = sentiment_pipeline(text[:512])[0]
    label = result["label"].lower()
    score = result["score"]
    if score < 0.6:
        return "neutral", score
    return label, score


def label_aspects(text, aspect_pipeline):
    if not isinstance(text, str) or text.strip() == "":
        return ["general"]

    result = aspect_pipeline(text[:512], candidate_labels=ASPECT_LABELS, multi_label=True)
    found = [
        label for label, score in zip(result["labels"], result["scores"])
        if score >= ASPECT_SCORE_THRESHOLD
    ]
    return found if found else ["general"]


def compute_severity(text, sentiment):
    if not isinstance(text, str):
        return False, 0.0
    matched = [pattern.pattern for pattern in SAFETY_PATTERNS if pattern.search(text)]
    if not matched:
        return False, 0.0
    score = min(1.0, len(matched) * 0.3)
    if sentiment == "negative":
        score = min(1.0, score + 0.2)
    return True, round(score, 2)


def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        return pd.read_csv(CHECKPOINT_PATH, low_memory=False)
    return None


def save_checkpoint(rows_done):
    pd.DataFrame(rows_done).to_csv(CHECKPOINT_PATH, index=False)


def run_labeling():
    df = pd.read_csv(RAW_PATH, low_memory=False)

    checkpoint_df = load_checkpoint()
    if checkpoint_df is not None:
        already_done = len(checkpoint_df)
        rows_done = checkpoint_df.to_dict("records")
        print(f"Resuming from checkpoint: {already_done} rows already processed")
    else:
        already_done = 0
        rows_done = []
        print("No checkpoint found, starting fresh")

    sentiment_pipeline = get_sentiment_pipeline()
    aspect_pipeline = get_aspect_pipeline()
    total_rows = len(df)

    for i in range(already_done, total_rows):
        row = df.iloc[i].to_dict()
        text = row["review_text"]

        sentiment, confidence = label_sentiment(text, sentiment_pipeline)
        aspects = label_aspects(text, aspect_pipeline)
        flag, severity = compute_severity(text, sentiment)

        row["sentiment"] = sentiment
        row["sentiment_confidence"] = confidence
        row["aspects"] = ", ".join(aspects)
        row["is_safety_issue"] = flag
        row["severity_score"] = severity

        rows_done.append(row)

        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(rows_done)
            print(f"Checkpoint saved: {i + 1} / {total_rows} rows")

    final_df = pd.DataFrame(rows_done)
    final_df.to_csv(LABELED_PATH, index=False)

    if os.path.exists(CHECKPOINT_PATH):
        os.remove(CHECKPOINT_PATH)

    print("Total flagged reviews:", int(final_df["is_safety_issue"].sum()))
    print("General-only aspect rows:", int((final_df["aspects"] == "general").sum()))
    print("Saved final labeled data to", LABELED_PATH)


if __name__ == "__main__":
    run_labeling()
