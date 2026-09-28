"""
ask.py

Command line entry point for the grounded question answering pipeline.

Run:
    python src/rag/ask.py --question "What do customers complain about regarding packaging?"
    python src/rag/ask.py --question "Any burning or rash reports?" --safety-only --max-rating 2
    python src/rag/ask.py --question "How is the price perceived?" --aspect price --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag.pipeline import answer_question
from rag.settings import TOP_K


def print_result(result):
    print(f"Status: {result['status']}")
    print(f"Answer: {result['answer']}")
    if result.get("cited_sources"):
        print("Cited reviews:")
        for r in result["cited_sources"]:
            snippet = " ".join(r["review_text"].split())[:110]
            print(f"  R{r['review_id']} | {r['rating']} stars | {r['submission_date']} | {r['product_name']} | {snippet}")
    if result.get("sources"):
        print(f"Retrieved {len(result['sources'])} reviews, cited {len(result['citations'])}")
    if result.get("invalid_citations"):
        print(f"Invalid citations: {result['invalid_citations']}")
    if result.get("unsupported_quotes"):
        print(f"Quotes not found in the excerpts: {result['unsupported_quotes']}")
    if result.get("injection_detected"):
        print("Note: a retrieved review contained instruction-like text and was treated as data.")
    if result.get("model"):
        print(f"Model: {result['model']}, {result['latency_sec']}s, "
              f"{result['prompt_tokens']} prompt tokens, {result['completion_tokens']} completion tokens")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--top-k", type=int, default=TOP_K)
    ap.add_argument("--aspect", default=None)
    ap.add_argument("--sentiment", default=None)
    ap.add_argument("--min-rating", type=int, default=None)
    ap.add_argument("--max-rating", type=int, default=None)
    ap.add_argument("--safety-only", action="store_true")
    ap.add_argument("--start-date", default=None)
    ap.add_argument("--end-date", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = answer_question(
        args.question, args.top_k, args.aspect, args.sentiment, args.min_rating,
        args.max_rating, args.safety_only, args.start_date, args.end_date,
    )
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_result(result)


if __name__ == "__main__":
    main()


