"""
settings.py

Central app settings: filesystem paths and environment-driven config. Every
other module that needs REPO_ROOT, REVIEWS_PATH, VECTORSTORE_DIR, or LOGS_DIR
imports it from here rather than recomputing it.

Fixed values (thresholds, model lists, retrieval parameters) live in constants.py.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from src.config.constants import PROVIDERS
from src.exceptions.exceptions import ConfigurationError


REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

REVIEWS_PATH = Path(os.environ.get(
    "REVIEWS_PATH",
    REPO_ROOT / "data" / "labeled" / "reviews_scrubbed.csv",
))

LABELED_REVIEWS_PATH = REPO_ROOT / "data" / "labeled" / "labeled_reviews.csv"
VECTORSTORE_DIR = REPO_ROOT / "data" / "vectorstore" / "chroma_db"
LOGS_DIR = REPO_ROOT / "logs"
REPORTS_DIR = REPO_ROOT / "reports"

API_TITLE = "Review Intelligence API"
API_VERSION = "0.1.0"

LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")


def resolve_model(model_spec):
    """Turn 'provider:model_id' into base_url, api_key and model id."""
    provider, _, model = model_spec.partition(":")
    if provider not in PROVIDERS or not model:
        raise ConfigurationError(
            f"Use provider:model_id with a provider from {list(PROVIDERS)}. Got '{model_spec}'."
        )
    config = PROVIDERS[provider]
    api_key = os.environ.get(config["key_env"])
    if not api_key:
        raise ConfigurationError(f"{config['key_env']} not found in .env")
    return {"provider": provider, "model": model, "base_url": config["base_url"], "api_key": api_key}


