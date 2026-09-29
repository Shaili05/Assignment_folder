"""
constants.py

Shared, centrally-defined constant values used across the backend. Any
number, threshold, or fixed list that more than one file needs (or that a
teammate might reasonably want to tune later) belongs here instead of being
re-declared in each file.
"""

AVAILABLE_MODELS = [
    "groq:openai/gpt-oss-120b",
    "groq:openai/gpt-oss-20b",
    "groq:qwen/qwen3.8-27b",
    "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
]

DEFAULT_MODEL = "groq:openai/gpt-oss-120b"

ASPECTS = ["packaging", "price", "texture_effectiveness", "availability"]
SENTIMENTS = ["positive", "neutral", "negative"]
SEVERITY_LEVELS = ["low", "medium", "high"]
ISSUE_TYPES = ["safety", "quality", "both"]

ROLE_LABELS = {
    "brand_manager": "Brand manager",
    "support_team": "Support team",
}

LOW_SAMPLE_THRESHOLD = 10          
MIN_PRODUCT_REVIEWS_FOR_TABLE = 3  

FLAGGED_REVIEW_EXCERPT_CHARS = 400   
SEARCH_RESULT_EXCERPT_CHARS = 600    



PROVIDERS = {
    "groq": {"base_url": "https://api.groq.com/openai/v1", "key_env": "GROQ_API_KEY"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key_env": "GOOGLE_API_KEY"},
    "nvidia": {"base_url": "https://integrate.api.nvidia.com/v1", "key_env": "NVIDIA_API_KEY"},
    "mistral": {"base_url": "https://api.mistral.ai/v1", "key_env": "MISTRAL_API_KEY"},
}

COLLECTION_NAME = "reviews"
EMBEDDING_MODEL_ID = "sentence-transformers/sentence-t5-base"
QUERY_PREFIX = ""
TOP_K = 5
MAX_TOP_K = 20


LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1500
LLM_MAX_RETRIES = 4
LLM_RETRY_BACKOFF_SEC = 5
LLM_FATAL_STATUS_CODES = (401, 403, 404)
MIN_QUOTE_CHARS = 12


PRICES = {
    "groq:openai/gpt-oss-120b": (0.15, 0.60),
    "groq:openai/gpt-oss-20b": (0.075, 0.30),
}
MAX_TURNS_PER_THREAD = 4


