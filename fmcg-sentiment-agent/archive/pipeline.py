"""
pipeline.py

Question -> guardrail check -> retrieval -> grounded answer.
Questions that cannot be answered from reviews return a status and a message
without calling the language model.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag.generator import generate_answer
from rag.guardrails import check_question
from rag.retriever import search_reviews
from rag.settings import TOP_K


def answer_question(question, top_k=TOP_K, aspect=None, sentiment=None, min_rating=None,
                    max_rating=None, safety_only=False, start_date=None, end_date=None, model=None):
    check = check_question(question)
    if check["status"] != "ok":
        return {"status": check["status"], "question": question, "answer": check["message"],
                "citations": [], "sources": [], "cited_sources": []}

    found = search_reviews(question, top_k, aspect, sentiment, min_rating, max_rating,
                           safety_only, start_date, end_date)
    if "error" in found:
        return {"status": "error", "question": question, "answer": found["error"],
                "citations": [], "sources": [], "cited_sources": []}
    if not found["reviews"]:
        return {"status": "no_results", "question": question,
                "answer": "No reviews matched the question and filters.",
                "citations": [], "sources": [], "cited_sources": []}

    result = generate_answer(question, found["reviews"], model)
    cited = set(result["citations"])
    result.update({
        "status": "answered",
        "question": question,
        "filters": found["filters"],
        "sources": found["reviews"],
        "cited_sources": [r for r in found["reviews"] if r["review_id"] in cited],
    })
    return result


