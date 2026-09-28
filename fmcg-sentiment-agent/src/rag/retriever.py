"""
retriever.py


Semantic search over the review vector store (ChromaDB, sentence-t5-base).
Every result carries the review id so answers can cite the exact reviews.
Reviewer identity fields are never returned.
"""

import numpy as np
import pandas as pd


from src.rag.guardrails import looks_like_injection
from src.rag.settings import (
    COLLECTION_NAME, EMBEDDING_MODEL_ID, EXCERPT_CHARS, MAX_TOP_K, QUERY_PREFIX, TOP_K, VECTORSTORE_DIR,
)

ASPECTS = ["packaging", "price", "texture_effectiveness", "availability"]
SENTIMENTS = ["positive", "neutral", "negative"]

_state = {}

def get_collection():
    if "collection" not in _state:
        import chromadb


        client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
        _state["collection"] = client.get_collection(COLLECTION_NAME)
    return _state["collection"]

def get_embedder():
    if "embedder" not in _state:
        from sentence_transformers import SentenceTransformer


        _state["embedder"] = SentenceTransformer(EMBEDDING_MODEL_ID)
    return _state["embedder"]


def embed_query(question):
    vector = get_embedder().encode([QUERY_PREFIX + question], convert_to_numpy=True).astype("float32")[0]
    norm = np.linalg.norm(vector)
    return (vector / norm if norm else vector).tolist()


def date_to_ts(value):
    return int(pd.Timestamp(value).strftime("%Y%m%d"))


def ts_to_date(ts):
    text = str(int(ts)) if ts else ""
    return f"{text[:4]}-{text[4:6]}-{text[6:8]}" if len(text) == 8 else None


def build_where(sentiment, min_rating, max_rating, safety_only, start_date, end_date):
    conditions = []
    if sentiment:
        conditions.append({"sentiment": sentiment})
    if min_rating is not None:
        conditions.append({"rating": {"$gte": int(min_rating)}})
    if max_rating is not None:
        conditions.append({"rating": {"$lte": int(max_rating)}})
    if safety_only:
        conditions.append({"is_safety_issue": True})
    if start_date:
        conditions.append({"submission_ts": {"$gte": date_to_ts(start_date)}})
    if end_date:
        conditions.append({"submission_ts": {"$lte": date_to_ts(end_date)}})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def search_reviews(question, top_k=TOP_K, aspect=None, sentiment=None, min_rating=None,
                   max_rating=None, safety_only=False, start_date=None, end_date=None):
    try:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")
        if aspect and aspect not in ASPECTS:
            raise ValueError(f"Unknown aspect '{aspect}'. Valid aspects: {', '.join(ASPECTS)}")
        if sentiment and sentiment not in SENTIMENTS:
            raise ValueError(f"sentiment must be one of: {', '.join(SENTIMENTS)}")
        top_k = max(1, min(int(top_k), MAX_TOP_K))
        where = build_where(sentiment, min_rating, max_rating, safety_only, start_date, end_date)
    except ValueError as exc:
        return {"error": str(exc)}


    n_results = top_k * 5 if aspect else top_k
    result = get_collection().query(
        query_embeddings=[embed_query(question)],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    reviews = []
    for rid, doc, meta, dist in zip(result["ids"][0], result["documents"][0],
                                    result["metadatas"][0], result["distances"][0]):
        if aspect and aspect not in meta.get("aspects", ""):
            continue
        reviews.append({
            "review_id": int(rid),
            "review_text": doc[:EXCERPT_CHARS],
            "rating": meta.get("rating"),
            "sentiment": meta.get("sentiment"),
            "aspects": meta.get("aspects"),
            "product_name": meta.get("product_name"),
            "brand_name": meta.get("brand_name"),
            "submission_date": ts_to_date(meta.get("submission_ts", 0)),
            "is_safety_issue": bool(meta.get("is_safety_issue", False)),
            "severity_level": meta.get("severity_level", ""),
            "similarity": round(1 - dist, 3),
            "instruction_like": looks_like_injection(doc),
        })
        if len(reviews) == top_k:
            break

    return {
        "tool": "search_reviews",
        "query": question,
        "filters": {
            "aspect": aspect, "sentiment": sentiment, "min_rating": min_rating, "max_rating": max_rating,
            "safety_only": safety_only, "start_date": start_date, "end_date": end_date,
        },
        "n_returned": len(reviews),
        "reviews": reviews,
    }
