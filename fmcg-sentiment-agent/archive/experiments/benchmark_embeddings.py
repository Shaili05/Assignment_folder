"""
benchmark_embeddings.py
Compares 5 sentence-embedding models across 2 vector store backends
(FAISS and ChromaDB) on a 1000-row stratified subsample of the
scrubbed, labeled reviews.

Why a subsample and not the full 6000 rows: 5 models x 2 stores on the
full set is too slow on CPU for the project timeline. A stratified
1000-row sample is representative enough to pick the best combo; the
winner then gets used to embed the full dataset in a separate,
production script.

How "best" is measured: there's no hand-labeled query-relevance data,
so the aspect/sentiment labels already generated are used as a proxy.
For a small set of aspect-anchored probe queries (packaging, price,
availability, texture/effectiveness, negative-general), we check what
fraction of the top-k retrieved reviews actually carry the matching
label. Embedding speed, index-build time and query latency are also
recorded since speed matters for the final tool.

MODELS and VECTOR_STORES below match config/config.yaml's
embedding_models and vector_stores sections, listed directly here so
this script doesn't need to read that file.

Run:
    python src/experiments/benchmark_embeddings.py --input data/labeled/reviews_scrubbed.csv --output data/experiments/embedding_benchmark_results.csv --sample-size 1000 --seed 42
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

MODELS = [
    "sentence-t5-base",
    "BAAI/bge-large-en",
    "intfloat/e5-small-v2",
    "paraphrase-multilingual-MiniLM-L12-v2",
    "all-MiniLM-L6-v2",
]


def _faiss_is_usable():
    # FAISS's compiled extension has been blocked on this machine by a
    # Windows Application Control policy. Detect that up front and fall
    # back to ChromaDB only, instead of crashing mid-run. The precision
    # benchmark showed FAISS and Chroma give equivalent results, so this
    # is a safe fallback.
    try:
        import faiss  # noqa: F401

        return True
    except Exception as exc:
        print(f"faiss import failed ({exc.__class__.__name__}), running with ChromaDB only")
        return False


VECTOR_STORES = ["chroma", "faiss"] if _faiss_is_usable() else ["chroma"]

PROBE_QUERIES = {
    "packaging": "complaints about the packaging, bottle, pump, or container",
    "price": "the product is too expensive or overpriced",
    "availability": "the product is sold out or hard to find in stores",
    "texture_effectiveness": "how the product feels on skin, its texture, scent, or how well it works",
    "negative_general": "a review expressing dissatisfaction or a bad experience",
}
TOP_K = 10

# Some models need specific prefix text on queries vs. documents to
# perform well (documented by their authors). Applying it keeps the
# benchmark fair instead of underrating e5/bge.
PREFIX_RULES = {
    "e5": ("query: ", "passage: "),
    "bge": ("Represent this sentence for searching relevant passages: ", ""),
}


def resolve_model_id(name):
    # Some models above are listed by short name but live under the
    # sentence-transformers org on HF. Only add the prefix if there's
    # no org in the name already.
    return name if "/" in name else f"sentence-transformers/{name}"


def get_prefixes(model_name):
    name_lower = model_name.lower()
    for key, (query_prefix, passage_prefix) in PREFIX_RULES.items():
        if key in name_lower:
            return query_prefix, passage_prefix
    return "", ""


def stratified_subsample(df, n, seed):
    frac = n / len(df)
    parts = [group.sample(frac=frac, random_state=seed) for _, group in df.groupby("rating")]
    sampled = pd.concat(parts, axis=0)
    if len(sampled) > n:
        sampled = sampled.sample(n=n, random_state=seed)
    return sampled.reset_index(drop=True)


def normalize(embeddings):
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1e-8
    return embeddings / norms


def precision_at_k(retrieved_rows, target, column):
    if column == "aspects":
        hits = retrieved_rows["aspects"].str.contains(target, case=False, na=False)
    else:
        hits = retrieved_rows[column] == target
    return hits.mean()


def build_faiss_index(embeddings):
    import faiss

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # vectors are pre-normalized, so inner product = cosine similarity
    index.add(embeddings)
    return index


def query_faiss(index, query_vec, k):
    _, ids = index.search(query_vec.reshape(1, -1), k)
    return ids[0].tolist()


def build_chroma_index(embeddings, row_ids):
    import chromadb

    client = chromadb.Client()  # in-memory, fine for a benchmark run
    collection = client.create_collection(
        name=f"bench_{int(time.time() * 1000)}",
        metadata={"hnsw:space": "cosine"},
    )
    collection.add(embeddings=embeddings.tolist(), ids=[str(i) for i in row_ids])
    return collection


def query_chroma(collection, query_vec, k):
    result = collection.query(query_embeddings=[query_vec.tolist()], n_results=k)
    return [int(i) for i in result["ids"][0]]


def run_benchmark(df, model_names, vector_stores):
    raw_texts = df["review_text"].tolist()
    results = []

    for config_name in model_names:
        model_id = resolve_model_id(config_name)
        query_prefix, passage_prefix = get_prefixes(config_name)

        print(f"\n=== Loading model: {config_name} (resolved: {model_id}) ===")
        model = SentenceTransformer(model_id)

        texts = [passage_prefix + t for t in raw_texts] if passage_prefix else raw_texts

        t0 = time.time()
        embeddings = model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True)
        embed_time = time.time() - t0
        embeddings = normalize(embeddings.astype("float32"))

        for store_name in vector_stores:
            print(f"--- Store: {store_name} ---")
            t0 = time.time()
            if store_name == "faiss":
                index = build_faiss_index(embeddings)
            else:
                index = build_chroma_index(embeddings, row_ids=df.index.tolist())
            build_time = time.time() - t0

            query_latencies, precisions = [], []
            for aspect_key, query_text in PROBE_QUERIES.items():
                prefixed_query = query_prefix + query_text if query_prefix else query_text
                q_vec = normalize(model.encode([prefixed_query], convert_to_numpy=True).astype("float32"))[0]

                t0 = time.time()
                if store_name == "faiss":
                    ids = query_faiss(index, q_vec, TOP_K)
                else:
                    ids = query_chroma(index, q_vec, TOP_K)
                query_latencies.append(time.time() - t0)

                retrieved = df.iloc[ids]
                if aspect_key == "negative_general":
                    p = precision_at_k(retrieved, "negative", "sentiment")
                else:
                    p = precision_at_k(retrieved, aspect_key, "aspects")
                precisions.append(p)

            results.append(
                {
                    "model": config_name,
                    "resolved_model_id": model_id,
                    "vector_store": store_name,
                    "embed_time_sec": round(embed_time, 2),
                    "index_build_time_sec": round(build_time, 3),
                    "avg_query_latency_ms": round(float(np.mean(query_latencies)) * 1000, 2),
                    "avg_precision_at_10": round(float(np.mean(precisions)), 3),
                }
            )

    return pd.DataFrame(results).sort_values("avg_precision_at_10", ascending=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/labeled/reviews_scrubbed.csv")
    ap.add_argument("--output", default="data/experiments/embedding_benchmark_results.csv")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    print(f"Models: {MODELS}")
    print(f"Vector stores: {VECTOR_STORES}")

    df = pd.read_csv(args.input, low_memory=False)
    print(f"Loaded {len(df)} scrubbed rows from {args.input}")

    sample_df = stratified_subsample(df, args.sample_size, args.seed)
    print(f"Benchmark subsample: {len(sample_df)} rows")

    results_df = run_benchmark(sample_df, MODELS, VECTOR_STORES)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(args.output, index=False)

    print("\nBenchmark results (best avg_precision_at_10 first)")
    print(results_df.to_string(index=False))
    print(f"\nWrote {args.output}")

    best = results_df.iloc[0]
    log_run(
        script_name="benchmark_embeddings.py",
        params=f"input={args.input}, sample_size={args.sample_size}, seed={args.seed}, models={MODELS}, stores={VECTOR_STORES}",
        summary=f"best={best['model']}/{best['vector_store']}, precision={best['avg_precision_at_10']}",
    )


if __name__ == "__main__":
    main()

