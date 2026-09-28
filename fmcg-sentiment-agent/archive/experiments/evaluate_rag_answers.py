"""
evaluate_rag_answers.py
Human-judged RAG evaluation. Instead of picking the best embedding
model + vector store from a retrieval precision@k proxy alone, this
script runs the full pipeline end to end (retrieve, then pass context
to the LLM, then generate an answer) for the same fixed set of
questions, across every model x store combination in
benchmark_embeddings.py's MODELS / VECTOR_STORES lists. Answers are
grouped by question in a plain-text report so they can be read side by
side and judged.

Reuses the embedding/index-building code from benchmark_embeddings.py
(same folder) so both scripts stay consistent.

LLM choice: labeling.py uses local HF models, no Groq calls there, so
this is a separate decision. This script uses Groq
(openai/gpt-oss-120b) for answer generation. Only ~60 calls are needed
for the full model x store x question grid, well inside the free-tier
daily limit, and a larger model here keeps generation quality out of
the way so differences between combos mostly reflect retrieval
quality, not LLM weakness.
(llama-3.3-70b-versatile was decommissioned by Groq on Aug 16, 2026;
openai/gpt-oss-120b is Groq's recommended replacement.)

Setup (on top of benchmark_embeddings.py's requirements):
    pip install groq python-dotenv

.env must contain:
    GROQ_API_KEY=your_key_here

Run:
    python src/experiments/evaluate_rag_answers.py --input data/labeled/reviews_scrubbed.csv --output-dir data/experiments --sample-size 1000 --seed 42 --top-k 5

Output:
    data/experiments/rag_answers.csv          one row per (question, model, store)
    data/experiments/rag_answers_report.md    same data, grouped by question
"""

import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from benchmark_embeddings import (
    MODELS,
    VECTOR_STORES,
    build_chroma_index,
    build_faiss_index,
    get_prefixes,
    normalize,
    query_chroma,
    query_faiss,
    resolve_model_id,
    stratified_subsample,
)
from questions import QUESTIONS as TEST_QUESTIONS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

GROQ_MODEL = "openai/gpt-oss-120b"

ANSWER_PROMPT_TEMPLATE = """You are a consumer-insights assistant. Answer the question using ONLY the review excerpts below. If the excerpts don't contain enough information, say so explicitly.

Review excerpts:
{context}

Question: {question}

Answer in 2-4 sentences, grounded strictly in the excerpts above."""


def build_context(retrieved_df):
    lines = []
    for _, row in retrieved_df.iterrows():
        lines.append(f"- (rating {row['rating']}/5) {row['review_text'][:300]}")
    return "\n".join(lines)


def generate_answer(client, question, context):
    prompt = ANSWER_PROMPT_TEMPLATE.format(context=context, question=question)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def run_evaluation(df, model_names, vector_stores, top_k, client, csv_path):
    raw_texts = df["review_text"].tolist()

    # Resume support: skip model/store combos already saved in csv_path,
    # so a crash mid-run doesn't lose everything. Re-embedding a large
    # model can take 5-10+ minutes.
    rows = []
    completed_combos = set()
    if Path(csv_path).exists():
        existing = pd.read_csv(csv_path)
        rows = existing.to_dict("records")
        completed_combos = set(zip(existing["model"], existing["vector_store"]))
        print(f"Resuming from {csv_path}: {len(completed_combos)} combo(s) already done, skipping them.")

    for config_name in model_names:
        if all((config_name, store) in completed_combos for store in vector_stores):
            print(f"\n=== Model: {config_name} (all stores already done, skipping) ===")
            continue

        model_id = resolve_model_id(config_name)
        query_prefix, passage_prefix = get_prefixes(config_name)

        print(f"\n=== Model: {config_name} ===")
        model = SentenceTransformer(model_id)

        texts = [passage_prefix + t for t in raw_texts] if passage_prefix else raw_texts
        embeddings = normalize(
            model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True).astype("float32")
        )

        for store_name in vector_stores:
            if (config_name, store_name) in completed_combos:
                print(f"--- Store: {store_name} (already done, skipping) ---")
                continue

            print(f"--- Store: {store_name} ---")
            if store_name == "faiss":
                index = build_faiss_index(embeddings)
            else:
                index = build_chroma_index(embeddings, row_ids=df.index.tolist())

            for question in TEST_QUESTIONS:
                prefixed_q = query_prefix + question if query_prefix else question
                q_vec = normalize(model.encode([prefixed_q], convert_to_numpy=True).astype("float32"))[0]

                if store_name == "faiss":
                    ids = query_faiss(index, q_vec, top_k)
                else:
                    ids = query_chroma(index, q_vec, top_k)

                retrieved = df.iloc[ids]
                context = build_context(retrieved)

                t0 = time.time()
                answer = generate_answer(client, question, context)
                gen_time = time.time() - t0

                rows.append(
                    {
                        "question": question,
                        "model": config_name,
                        "vector_store": store_name,
                        "answer": answer,
                        "gen_time_sec": round(gen_time, 2),
                        "retrieved_review_ids": ",".join(str(i) for i in ids),
                    }
                )
                print(f"  Q: {question[:50]}... -> answered ({gen_time:.1f}s)")

            pd.DataFrame(rows).to_csv(csv_path, index=False)
            print(f"  Progress saved to {csv_path}")

    return pd.DataFrame(rows)


def write_report(results_df, path):
    # Plain text, no markdown bold emphasis -- easier to scan and diff
    # than **bolded** headers.
    lines = ["RAG Answer Comparison Report", "=" * 40, ""]
    for question in results_df["question"].unique():
        lines.append(question)
        lines.append("-" * len(question))
        subset = results_df[results_df["question"] == question]
        for _, row in subset.iterrows():
            lines.append(f"Model: {row['model']} | Store: {row['vector_store']} | Time: {row['gen_time_sec']}s")
            lines.append(row["answer"])
            lines.append("")
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/labeled/reviews_scrubbed.csv")
    ap.add_argument("--output-dir", default="data/experiments")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args()

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY not found -- add it to your .env file.")
    client = Groq(api_key=api_key)

    df = pd.read_csv(args.input, low_memory=False)
    sample_df = stratified_subsample(df, args.sample_size, args.seed)
    total_calls = len(MODELS) * len(VECTOR_STORES) * len(TEST_QUESTIONS)
    print(
        f"Evaluating on {len(sample_df)}-row subsample, "
        f"{len(MODELS)} models x {len(VECTOR_STORES)} stores x {len(TEST_QUESTIONS)} questions "
        f"= {total_calls} LLM calls"
    )

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    csv_path = Path(args.output_dir) / "rag_answers.csv"
    report_path = Path(args.output_dir) / "rag_answers_report.txt"

    results_df = run_evaluation(sample_df, MODELS, VECTOR_STORES, args.top_k, client, csv_path)

    write_report(results_df, str(report_path))

    print(f"\nWrote {csv_path}")
    print(f"Wrote {report_path} -- open this to read answers grouped by question and judge the best combo.")

    log_run(
        script_name="evaluate_rag_answers.py",
        params=f"input={args.input}, sample_size={args.sample_size}, seed={args.seed}, top_k={args.top_k}, models={MODELS}, stores={VECTOR_STORES}",
        summary=f"answers_generated={len(results_df)}, questions={len(TEST_QUESTIONS)}",
    )


if __name__ == "__main__":
    main()

