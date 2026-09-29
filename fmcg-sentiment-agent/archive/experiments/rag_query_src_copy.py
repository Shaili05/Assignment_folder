"""
rag_query.py
The actual RAG tool. Takes a question, retrieves relevant reviews from
the production vector store, and generates a grounded answer via Groq.

Uses the persistent ChromaDB collection built by
build_production_vectorstore.py (all 6000 reviews, sentence-t5-base
embeddings). Supports optional filters (rating range, aspect,
safety-flagged only) since that metadata was stored specifically for
this.

Setup:
    pip install chromadb sentence-transformers groq python-dotenv

Run (interactive):
    python src/experiments/rag_query.py

Run (single question):
    python src/experiments/rag_query.py --question "What do customers say about packaging?"

Run (with filters):
    python src/experiments/rag_query.py --question "..." --safety-only
    python src/experiments/rag_query.py --question "..." --min-rating 4
    python src/experiments/rag_query.py --question "..." --aspect price
"""


import argparse
import os
import sys
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from benchmark_embeddings import get_prefixes, normalize, resolve_model_id

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

MODEL_NAME = "sentence-t5-base"
GROQ_MODEL = "openai/gpt-oss-120b"
VECTORSTORE_DIR = "data/vectorstore/chroma_db"
COLLECTION_NAME = "reviews"
TOP_K = 5

ANSWER_PROMPT_TEMPLATE = """You are a consumer-insights assistant. Answer the question using ONLY the review excerpts below. If the excerpts don't contain enough information, say so explicitly.

Review excerpts:
{context}

Question: {question}

Answer in 2-4 sentences, grounded strictly in the excerpts above."""


def load_vectorstore():
    client = chromadb.PersistentClient(path=VECTORSTORE_DIR)
    return client.get_collection(COLLECTION_NAME)


def build_where_filter(min_rating, max_rating, safety_only):
    conditions = []
    if min_rating is not None:
        conditions.append({"rating": {"$gte": min_rating}})
    if max_rating is not None:
        conditions.append({"rating": {"$lte": max_rating}})
    if safety_only:
        conditions.append({"is_safety_issue": True})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def build_context(documents, metadatas):
    lines = []
    for doc, meta in zip(documents, metadatas):
        lines.append(f"- (rating {meta.get('rating')}/5) {doc[:300]}")
    return "\n".join(lines)


def answer_question(collection, model, groq_client, question, query_prefix, min_rating, max_rating, aspect, safety_only, top_k):
    prefixed_q = query_prefix + question if query_prefix else question
    q_vec = normalize(model.encode([prefixed_q], convert_to_numpy=True).astype("float32"))[0]

    where = build_where_filter(min_rating, max_rating, safety_only)
    # aspects is stored as a free-text comma-joined string, so it can't
    # be an exact-match where-filter -- over-fetch and filter after.
    n_results = top_k * 4 if aspect else top_k

    result = collection.query(query_embeddings=[q_vec.tolist()], n_results=n_results, where=where)

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]

    if aspect:
        pairs = [(d, m) for d, m in zip(documents, metadatas) if aspect.lower() in m.get("aspects", "").lower()]
        pairs = pairs[:top_k]
        documents = [d for d, _ in pairs]
        metadatas = [m for _, m in pairs]

    if not documents:
        return "No reviews matched the given question and filters.", []

    context = build_context(documents, metadatas)
    prompt = ANSWER_PROMPT_TEMPLATE.format(context=context, question=question)
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip(), metadatas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", default=None)
    ap.add_argument("--top-k", type=int, default=TOP_K)
    ap.add_argument("--min-rating", type=int, default=None)
    ap.add_argument("--max-rating", type=int, default=None)
    ap.add_argument("--aspect", default=None, choices=["packaging", "price", "texture_effectiveness", "availability"])
    ap.add_argument("--safety-only", action="store_true")
    args = ap.parse_args()

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY not found -- add it to your .env file.")
    groq_client = Groq(api_key=api_key)

    print("Loading vector store...")
    collection = load_vectorstore()
    print(f"Loaded collection with {collection.count()} reviews")

    model_id = resolve_model_id(MODEL_NAME)
    query_prefix, _ = get_prefixes(MODEL_NAME)
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(model_id)

    if args.question:
        answer, sources = answer_question(
            collection, model, groq_client, args.question, query_prefix,
            args.min_rating, args.max_rating, args.aspect, args.safety_only, args.top_k,
        )
        print(f"\nQuestion: {args.question}")
        print(f"Answer: {answer}")
        print(f"Sources used: {len(sources)} reviews")

        log_run(
            script_name="rag_query.py",
            params=f"question={args.question!r}, top_k={args.top_k}, min_rating={args.min_rating}, max_rating={args.max_rating}, aspect={args.aspect}, safety_only={args.safety_only}",
            summary=f"sources_used={len(sources)}",
        )
        return

    print("\nInteractive mode -- type a question, or 'quit' to exit.")
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        answer, sources = answer_question(
            collection, model, groq_client, question, query_prefix,
            None, None, None, False, TOP_K,
        )
        print(f"Answer: {answer}")
        print(f"(based on {len(sources)} reviews)")

        log_run(
            script_name="rag_query.py",
            params=f"question={question!r}, top_k={TOP_K}",
            summary=f"sources_used={len(sources)}",
        )

if __name__ == "__main__":
    main()