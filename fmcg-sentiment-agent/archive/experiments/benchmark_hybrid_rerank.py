"""
benchmark_hybrid_rerank.py
Tests whether hybrid retrieval (BM25 keyword search + embeddings) plus
cross-encoder reranking beats the chosen baseline (sentence-t5-base +
Chroma alone) on retrieval precision. Uses the same 1000-row sample and
same probe queries as benchmark_embeddings.py, so the result is a
direct, apples-to-apples comparison against the existing 0.42 baseline
-- not a new, incomparable number.

Approach tested:
1. Embed the corpus with sentence-t5-base (same model as production).
2. Build a BM25 index over the same corpus (keyword/lexical search).
3. For each probe query: get top-20 from embeddings, top-20 from BM25,
   combine them with reciprocal rank fusion, then rerank the combined
   candidates with a cross-encoder and keep the top-10.
4. Score with the same precision_at_k function used in
   benchmark_embeddings.py, so results are directly comparable.

Setup (on top of benchmark_embeddings.py's requirements):
    pip install rank_bm25

Run:
    python src/experiments/benchmark_hybrid_rerank.py --input data/labeled/reviews_scrubbed.csv --sample-size 1000 --seed 42
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from benchmark_embeddings import (
    MODELS,
    PROBE_QUERIES,
    build_chroma_index,
    get_prefixes,
    normalize,
    precision_at_k,
    query_chroma,
    resolve_model_id,
    stratified_subsample,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

MODEL_NAME = "sentence-t5-base"  # the chosen production model
RERANKER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
TOP_K_FINAL = 10
TOP_K_CANDIDATES = 20  # each of BM25 and embeddings contributes this many before fusion
RRF_K = 60  # standard reciprocal rank fusion constant


def build_bm25_index(texts):
    tokenized = [t.lower().split() for t in texts]
    return BM25Okapi(tokenized)


def bm25_top_n(bm25, query, n):
    scores = bm25.get_scores(query.lower().split())
    ranked = np.argsort(scores)[::-1][:n]
    return ranked.tolist()


def reciprocal_rank_fusion(rankings, k=RRF_K):
    # rankings: list of ranked-id-lists (each already best-first).
    # Each list contributes 1/(k + rank) to a doc's fused score.
    fused_scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(fused_scores, key=fused_scores.get, reverse=True)


def rerank(cross_encoder, query, candidate_ids, texts, top_n):
    pairs = [[query, texts[i]] for i in candidate_ids]
    scores = cross_encoder.predict(pairs)
    order = np.argsort(scores)[::-1][:top_n]
    return [candidate_ids[i] for i in order]


def run_baseline(df, model, query_prefix, embeddings):
    index = build_chroma_index(embeddings, row_ids=df.index.tolist())
    precisions = []
    for aspect_key, query_text in PROBE_QUERIES.items():
        prefixed_query = query_prefix + query_text if query_prefix else query_text
        q_vec = normalize(model.encode([prefixed_query], convert_to_numpy=True).astype("float32"))[0]
        ids = query_chroma(index, q_vec, TOP_K_FINAL)
        retrieved = df.iloc[ids]
        target = "negative" if aspect_key == "negative_general" else aspect_key
        col = "sentiment" if aspect_key == "negative_general" else "aspects"
        precisions.append(precision_at_k(retrieved, target, col))
    return float(np.mean(precisions))


def run_hybrid_rerank(df, model, query_prefix, embeddings, bm25, cross_encoder, raw_texts):
    index = build_chroma_index(embeddings, row_ids=df.index.tolist())
    precisions = []
    for aspect_key, query_text in PROBE_QUERIES.items():
        prefixed_query = query_prefix + query_text if query_prefix else query_text
        q_vec = normalize(model.encode([prefixed_query], convert_to_numpy=True).astype("float32"))[0]

        embed_ids = query_chroma(index, q_vec, TOP_K_CANDIDATES)
        bm25_ids = bm25_top_n(bm25, query_text, TOP_K_CANDIDATES)
        fused_ids = reciprocal_rank_fusion([embed_ids, bm25_ids])[:TOP_K_CANDIDATES]

        final_ids = rerank(cross_encoder, query_text, fused_ids, raw_texts, TOP_K_FINAL)

        retrieved = df.iloc[final_ids]
        target = "negative" if aspect_key == "negative_general" else aspect_key
        col = "sentiment" if aspect_key == "negative_general" else "aspects"
        precisions.append(precision_at_k(retrieved, target, col))
    return float(np.mean(precisions))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/labeled/reviews_scrubbed.csv")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.input, low_memory=False)
    sample_df = stratified_subsample(df, args.sample_size, args.seed)
    print(f"Testing on {len(sample_df)}-row subsample")

    model_id = resolve_model_id(MODEL_NAME)
    query_prefix, passage_prefix = get_prefixes(MODEL_NAME)
    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(model_id)

    raw_texts = sample_df["review_text"].tolist()
    texts_for_embedding = [passage_prefix + t for t in raw_texts] if passage_prefix else raw_texts
    embeddings = normalize(
        model.encode(texts_for_embedding, batch_size=32, show_progress_bar=True, convert_to_numpy=True).astype("float32")
    )

    print("Building BM25 index")
    bm25 = build_bm25_index(raw_texts)

    print(f"Loading reranker: {RERANKER_NAME}")
    cross_encoder = CrossEncoder(RERANKER_NAME)

    print("\nScoring baseline (embeddings only, current production setup)...")
    baseline_precision = run_baseline(sample_df, model, query_prefix, embeddings)

    print("Scoring hybrid + rerank...")
    hybrid_precision = run_hybrid_rerank(sample_df, model, query_prefix, embeddings, bm25, cross_encoder, raw_texts)

    improvement = hybrid_precision - baseline_precision
    relative = (improvement / baseline_precision * 100) if baseline_precision > 0 else 0.0

    print("\n=== Result ===")
    print(f"Baseline (embeddings only):     {baseline_precision:.3f}")
    print(f"Hybrid + rerank:                {hybrid_precision:.3f}")
    print(f"Absolute change:                {improvement:+.3f}")
    print(f"Relative change:                {relative:+.1f}%")

    log_run(
        script_name="benchmark_hybrid_rerank.py",
        params=f"input={args.input}, sample_size={args.sample_size}, seed={args.seed}, model={MODEL_NAME}, reranker={RERANKER_NAME}",
        summary=f"baseline_precision={baseline_precision:.3f}, hybrid_rerank_precision={hybrid_precision:.3f}, relative_change={relative:+.1f}%",
    )


if __name__ == "__main__":
    main()

