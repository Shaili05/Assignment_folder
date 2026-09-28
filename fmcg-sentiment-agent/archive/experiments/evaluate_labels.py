"""
evaluate_labels.py

Measures labeling accuracy against the hand-labeled gold set.

Compared labelers:
  local        sentiment / aspects / safety flag from the labeling pipeline
  llm          few-shot LLM labels from llm_label_gold.py
  rating_rule  sentiment derived from the star rating (1-2 negative,
               3 neutral, 4-5 positive), used as a cheap baseline

Sentiment and aspect scores are reported on all gold rows and on the random
subset only (the random subset is the representative one). Issue scores use
all rows, since that sample deliberately over-represents flagged reviews.

Outputs:
  data/gold/label_accuracy_report.csv
  data/gold/label_disagreements.csv

Run:
    python src/data_prep/evaluate_labels.py
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

SENTIMENTS = ["positive", "negative", "neutral"]
ASPECTS = ["packaging", "price", "texture_effectiveness", "availability"]
ISSUES = {"none", "safety", "quality", "both"}
MIN_VALID_ROWS = 30


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def aspect_tokens(value):
    return {token.strip() for token in clean(value).split(",") if token.strip()}


def aspect_set(value):
    return aspect_tokens(value) & set(ASPECTS)


def rating_to_sentiment(rating):
    if rating <= 2:
        return "negative"
    if rating == 3:
        return "neutral"
    return "positive"


def safe_divide(a, b):
    return a / b if b else 0.0


def macro_f1(y_true, y_pred, classes):
    scores = []
    for cls in classes:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p == cls)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != cls and p == cls)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p != cls)
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        scores.append(safe_divide(2 * precision * recall, precision + recall))
    return sum(scores) / len(scores)


def binary_scores(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
    fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "support": tp + fn,
        "precision": precision,
        "recall": recall,
        "f1": safe_divide(2 * precision * recall, precision + recall),
    }


def load_data(args):
    gold = pd.read_csv(args.gold)
    meta = pd.read_csv(args.meta)
    reviews = pd.read_csv(args.reviews, low_memory=False)
    llm = pd.read_csv(args.llm)

    df = gold.merge(meta, on="review_id").merge(llm, on="review_id", how="left")

    stored_ratings = reviews.loc[df["review_id"], "rating"].values
    if not (stored_ratings == df["rating"].values).all():
        raise SystemExit("Gold review_ids do not match the reviews file. Check the input paths.")

    local = reviews.loc[df["review_id"]].reset_index(drop=True)
    df["local_sentiment"] = local["sentiment"].map(clean)
    df["local_aspects"] = local["aspects"]
    df["local_flag"] = local["is_safety_issue"].astype(bool)
    return df


def validate_gold(df):
    df["gold_sentiment"] = df["gold_sentiment"].map(clean)
    df["gold_issue"] = df["gold_issue"].map(clean)

    bad_sentiment = ~df["gold_sentiment"].isin(SENTIMENTS)
    bad_issue = ~df["gold_issue"].isin(ISSUES)
    bad_aspects = df["gold_aspects"].map(lambda v: not aspect_tokens(v) or not aspect_tokens(v) <= set(ASPECTS + ["general"]))
    invalid = bad_sentiment | bad_issue | bad_aspects

    if invalid.any():
        ids = df.loc[invalid, "review_id"].tolist()
        print(f"Skipped {int(invalid.sum())} rows with missing or invalid gold labels: {ids[:15]}")

    valid = df[~invalid].copy()
    if len(valid) < MIN_VALID_ROWS:
        raise SystemExit(f"Only {len(valid)} valid gold rows, need at least {MIN_VALID_ROWS}.")
    return valid


def sentiment_rows(df, subset):
    rows = []
    predictions = {
        "local": df["local_sentiment"],
        "llm": df["llm_sentiment"].map(clean),
        "rating_rule": df["rating"].map(rating_to_sentiment),
    }
    for name, pred in predictions.items():
        mask = pred.isin(SENTIMENTS)
        y_true = df.loc[mask, "gold_sentiment"].tolist()
        y_pred = pred[mask].tolist()
        rows.append({
            "task": "sentiment",
            "labeler": name,
            "subset": subset,
            "n": len(y_true),
            "accuracy": safe_divide(sum(t == p for t, p in zip(y_true, y_pred)), len(y_true)),
            "macro_f1": macro_f1(y_true, y_pred, SENTIMENTS),
        })
    return rows


def aspect_rows(df, subset):
    rows = []
    predictions = {"local": df["local_aspects"], "llm": df["llm_aspects"]}
    gold_sets = df["gold_aspects"].map(aspect_set)

    for name, pred in predictions.items():
        mask = pred.notna()
        pred_sets = pred[mask].map(aspect_set)
        truth_sets = gold_sets[mask]

        exact = safe_divide(sum(t == p for t, p in zip(truth_sets, pred_sets)), len(truth_sets))
        rows.append({"task": "aspect_exact_match", "labeler": name, "subset": subset, "n": len(truth_sets), "accuracy": exact})

        for aspect in ASPECTS:
            scores = binary_scores([aspect in t for t in truth_sets], [aspect in p for p in pred_sets])
            rows.append({"task": f"aspect_{aspect}", "labeler": name, "subset": subset, "n": len(truth_sets), **scores})
    return rows


def issue_rows(df):
    rows = []
    truth = (df["gold_issue"] != "none").tolist()
    predictions = {
        "rules": df["local_flag"].tolist(),
        "llm": (df["llm_issue"].map(clean).isin(["safety", "quality", "both"])).tolist(),
    }
    for name, pred in predictions.items():
        rows.append({"task": "issue_flag", "labeler": name, "subset": "all", "n": len(truth), **binary_scores(truth, pred)})
    return rows


def build_disagreements(df):
    gold_aspects = df["gold_aspects"].map(aspect_set)
    local_aspects = df["local_aspects"].map(aspect_set)
    llm_aspects = df["llm_aspects"].map(aspect_set)
    llm_issue = df["llm_issue"].map(clean)

    wrong = (
        (df["local_sentiment"] != df["gold_sentiment"])
        | (df["llm_sentiment"].map(clean) != df["gold_sentiment"])
        | (local_aspects != gold_aspects)
        | (llm_aspects != gold_aspects)
        | (df["local_flag"] != (df["gold_issue"] != "none"))
        | ((llm_issue != "none") != (df["gold_issue"] != "none"))
    )

    out = pd.DataFrame({
        "review_id": df["review_id"],
        "sample_type": df["sample_type"],
        "rating": df["rating"],
        "review_text": df["review_text"].str.slice(0, 250),
        "gold_sentiment": df["gold_sentiment"],
        "local_sentiment": df["local_sentiment"],
        "llm_sentiment": df["llm_sentiment"],
        "gold_aspects": df["gold_aspects"],
        "local_aspects": df["local_aspects"],
        "llm_aspects": df["llm_aspects"],
        "gold_issue": df["gold_issue"],
        "rule_flag": df["local_flag"],
        "llm_issue": df["llm_issue"],
    })
    return out[wrong]


def show(title, table):
    print(title)
    print(table.to_string(index=False))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default="data/gold/gold_set_template.csv")
    ap.add_argument("--meta", default="data/gold/gold_set_meta.csv")
    ap.add_argument("--reviews", default="data/labeled/reviews_scrubbed.csv")
    ap.add_argument("--llm", default="data/gold/llm_labels_gold.csv")
    ap.add_argument("--report", default="data/gold/label_accuracy_report.csv")
    ap.add_argument("--disagreements", default="data/gold/label_disagreements.csv")
    args = ap.parse_args()

    df = validate_gold(load_data(args))
    random_df = df[df["sample_type"] == "random"]
    print(f"Valid gold rows: {len(df)} (random subset: {len(random_df)})")
    print()

    rows = []
    rows += sentiment_rows(df, "all")
    rows += sentiment_rows(random_df, "random")
    rows += aspect_rows(df, "all")
    rows += aspect_rows(random_df, "random")
    rows += issue_rows(df)
    report = pd.DataFrame(rows)

    sentiment = report[report["task"] == "sentiment"][["labeler", "subset", "n", "accuracy", "macro_f1"]]
    show("Sentiment", sentiment.round(3))

    print("Local sentiment confusion matrix (rows = gold, columns = local), all rows")
    print(pd.crosstab(df["gold_sentiment"], df["local_sentiment"]).to_string())
    print()

    exact = report[report["task"] == "aspect_exact_match"][["labeler", "subset", "n", "accuracy"]]
    show("Aspect exact match", exact.round(3))

    per_aspect = report[report["task"].str.startswith("aspect_") & (report["task"] != "aspect_exact_match")]
    per_aspect = per_aspect[per_aspect["subset"] == "all"][["task", "labeler", "support", "precision", "recall", "f1"]]
    show("Aspect precision and recall, all rows", per_aspect.round(3))

    issue = report[report["task"] == "issue_flag"][["labeler", "n", "support", "tp", "fp", "fn", "precision", "recall", "f1"]]
    show("Safety and quality flag, all rows", issue.round(3))

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    report.round(4).to_csv(args.report, index=False)
    disagreements = build_disagreements(df)
    disagreements.to_csv(args.disagreements, index=False, encoding="utf-8-sig")
    print(f"Wrote {args.report}")
    print(f"Wrote {args.disagreements} ({len(disagreements)} rows)")

    headline = sentiment[sentiment["subset"] == "random"].set_index("labeler")["accuracy"].round(3).to_dict()
    log_run(
        script_name="evaluate_labels.py",
        params=f"gold={args.gold}, llm={args.llm}",
        summary=f"valid_rows={len(df)}, random_sentiment_accuracy={headline}",
    )


if __name__ == "__main__":
    main()