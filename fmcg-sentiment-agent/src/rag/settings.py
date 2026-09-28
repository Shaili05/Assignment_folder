"""
settings.py

RAG/LLM-specific configuration. Shared paths (REPO_ROOT, REVIEWS_PATH) come
from src.config.settings, which is the single place those are defined.
"""

import os

from src.config.settings import REPO_ROOT

VECTORSTORE_DIR = REPO_ROOT / "data" / "vectorstore" / "chroma_db"
COLLECTION_NAME = "reviews"

EMBEDDING_MODEL_ID = "sentence-transformers/sentence-t5-base"
QUERY_PREFIX = ""

LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1500

TOP_K = 5
MAX_TOP_K = 20
EXCERPT_CHARS = 600
