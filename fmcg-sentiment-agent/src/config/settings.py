"""
settings.py

Central app settings: filesystem paths and environment-driven config. Every
other module that needs REPO_ROOT, REVIEWS_PATH, VECTORSTORE_DIR, or LOGS_DIR
imports it from here rather than recomputing it.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

REVIEWS_PATH = Path(os.environ.get(
    "REVIEWS_PATH",
    REPO_ROOT / "data" / "labeled" / "reviews_scrubbed.csv",
))

VECTORSTORE_DIR = REPO_ROOT / "data" / "vectorstore" / "chroma_db"
LOGS_DIR = REPO_ROOT / "logs"
REPORTS_DIR = REPO_ROOT / "reports"

API_TITLE = "Review Intelligence API"
API_VERSION = "0.1.0"


