"""
validate_production_questions.py
Runs the full 10-question set (questions.py) through the actual
production system -- the final chosen model (sentence-t5-base) and
vector store (ChromaDB), same as rag_query.py uses. This is much
cheaper than re-running the full 5-model x 2-store benchmark, since the
model/store decision is already finalized -- this just confirms the
deployed system handles the wider question set well, including the new
edge cases (positive feedback, out-of-scope/hallucination check, vague
query, narrow filtering).

Run:
    python src/experiments/validate_production_questions.py
"""

import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from questions import QUESTIONS
from rag_query import answer_question, load_vectorstore
from benchmark_embeddings import get_prefixes, resolve_model_id

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.run_log import log_run

import os

MODEL_NAME = "sentence-t5-base"


def main():
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY not found -- add it to your .env file.")
    groq_client = Groq(api_key=api_key)

    print("Loading production vector store...")
    collection = load_vectorstore()
    print(f"Loaded collection with {collection.count()} reviews")

    model_id = resolve_model_id(MODEL_NAME)
    query_prefix, _ = get_prefixes(MODEL_NAME)
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(model_id)

    rows = []
    for question in QUESTIONS:
        answer, sources = answer_question(
            collection, model, groq_client, question, query_prefix,
            None, None, None, False, 5,
        )
        rows.append({"question": question, "answer": answer, "sources_used": len(sources)})
        print(f"\nQ: {question}")
        print(f"A: {answer}")
        print(f"(based on {len(sources)} reviews)")

    results_df = pd.DataFrame(rows)
    output_path = Path("data/experiments/production_questions_report.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)
    print(f"\nWrote {output_path}")

    log_run(
        script_name="validate_production_questions.py",
        params=f"model={MODEL_NAME}, question_count={len(QUESTIONS)}",
        summary=f"answers_generated={len(results_df)}",
    )


if __name__ == "__main__":
    main()

