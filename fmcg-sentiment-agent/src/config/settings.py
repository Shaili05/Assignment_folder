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
EVALUATION_DIR = REPO_ROOT / "data" / "evaluation"
EVAL_RESULTS_PATH = EVALUATION_DIR / "results.csv"
EVAL_SUMMARY_PATH = EVALUATION_DIR / "summary.csv"
EVAL_AUDIT_PATH = LOGS_DIR / "evaluation_audit.jsonl"
AUDIT_LOG_PATH = LOGS_DIR / "audit_log.jsonl"
PROGRESS_LOG_PATH = LOGS_DIR / "progress_log.jsonl"
RUN_LOG_PATH = LOGS_DIR / "run_log.csv"
CHAT_STORE_PATH = LOGS_DIR / "chat_sessions.json"


API_TITLE = "Review Intelligence API"
API_VERSION = "0.1.0"
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")

LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")


def resolve_model(model_spec):
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
