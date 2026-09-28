"""
build_production_vectorstore.py
Embeds the full scrubbed review set (all 6000 rows, not a subsample)
with the winning model from benchmarking + RAG evaluation, and builds a
persistent ChromaDB collection on disk so the RAG pipeline and tool can
load it directly without re-embedding every time.

Winning combo (see EXPERIMENT_LOG.md section 6 for full reasoning):
    Model:        sentence-transformers/sentence-t5-base
    Vector store: ChromaDB (persistent), chosen over FAISS for
                  reliability -- FAISS's compiled extension was blocked
                  twice by a Windows Application Control policy during
                  experimentation on this machine.

This is a one-time script. Run it once and data/vectorstore/ becomes
the source of truth for the RAG pipeline. Expect roughly 45-70 minutes
for 6000 rows on CPU (sentence-t5-base was the slowest model in
benchmarking, about 637s per 1000 rows there).

Run:
    python src/experiments/build_production_vectorstore.py --input data/labeled/reviews_scrubbed.csv --output-dir data/vectorstore/chroma_db
"""

import argparse
import sys
from pathlib import Path

import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

from benchmark_embeddings import get_prefixes, normalize, resolve_model_id

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

MODEL_NAME = "sentence-t5-base"

# Carried alongside each vector so the RAG pipeline can filter retrieval
# by rating, aspect, sentiment, safety flag, product, etc. without a
# separate lookup.
METADATA_COLUMNS = [
    "rating",
    "aspects",
    "sentiment",
    "is_safety_issue",
    "product_name",
    "brand_name",
    "user_id",
]


def build_metadata(df):
    # Chroma metadata values must be str/int/float/bool -- NaN becomes
    # empty string, everything else passes through as-is.
    records = []
    for _, row in df.iterrows():
        record = {}
        for col in METADATA_COLUMNS:
            value = row[col]
            if pd.isna(value):
                record[col] = ""
            elif isinstance(value, bool):
                record[col] = bool(value)
            else:
                record[col] = value
        records.append(record)
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/labeled/reviews_scrubbed.csv")
    ap.add_argument("--output-dir", default="data/vectorstore/chroma_db")
    ap.add_argument("--collection-name", default="reviews")
    args = ap.parse_args()

    df = pd.read_csv(args.input, low_memory=False)
    print(f"Loaded {len(df)} rows from {args.input}")

    model_id = resolve_model_id(MODEL_NAME)
    query_prefix, passage_prefix = get_prefixes(MODEL_NAME)
    print(f"Loading model: {MODEL_NAME} (resolved: {model_id})")
    model = SentenceTransformer(model_id)

    raw_texts = df["review_text"].tolist()
    texts_for_embedding = [passage_prefix + t for t in raw_texts] if passage_prefix else raw_texts

    print(f"Embedding {len(texts_for_embedding)} reviews, expect roughly 45-70 min...")
    embeddings = normalize(
        model.encode(texts_for_embedding, batch_size=32, show_progress_bar=True, convert_to_numpy=True).astype("float32")
    )

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=args.output_dir)

    existing_names = [c.name for c in client.list_collections()]
    if args.collection_name in existing_names:
        client.delete_collection(args.collection_name)
        print(f"Replaced existing collection '{args.collection_name}'")

    collection = client.create_collection(name=args.collection_name, metadata={"hnsw:space": "cosine"})

    metadatas = build_metadata(df)
    ids = [str(i) for i in df.index]

    BATCH = 500
    for start in range(0, len(df), BATCH):
        end = min(start + BATCH, len(df))
        collection.add(
            embeddings=embeddings[start:end].tolist(),
            documents=raw_texts[start:end],
            metadatas=metadatas[start:end],
            ids=ids[start:end],
        )
        print(f"  Inserted {end} / {len(df)} rows")

    print(f"\nDone. Persistent Chroma collection '{args.collection_name}' saved to {args.output_dir}")
    print(f"Total vectors stored: {collection.count()}")
    print(f"Query prefix to use at retrieval time (if any): {query_prefix!r}")

    log_run(
        script_name="build_production_vectorstore.py",
        params=f"input={args.input}, output_dir={args.output_dir}, model={MODEL_NAME}",
        summary=f"vectors_stored={collection.count()}, collection={args.collection_name}",
    )


if __name__ == "__main__":
    main()

