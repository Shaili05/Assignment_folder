"""
constants.py

Shared, centrally-defined constant values used across the backend. Any
number, threshold, or fixed list that more than one file needs (or that a
teammate might reasonably want to tune later) belongs here instead of being
re-declared in each file.
"""

# --- Agent / model configuration ---
AVAILABLE_MODELS = [
    "groq:openai/gpt-oss-120b",
    "groq:openai/gpt-oss-20b",
    "groq:qwen/qwen3.8-27b",
    "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
]

DEFAULT_FRAMEWORK = "langgraph"
DEFAULT_MODEL = "groq:openai/gpt-oss-120b"

# --- Review data enums (mirror what review_repository.py derives from the data) ---
ASPECTS = ["packaging", "price", "texture_effectiveness", "availability"]
SENTIMENTS = ["positive", "neutral", "negative"]
SEVERITY_LEVELS = ["low", "medium", "high"]
ISSUE_TYPES = ["safety", "quality", "both"]

# --- Roles ---
ROLE_LABELS = {
    "brand_manager": "Brand manager",
    "support_team": "Support team",
}

# --- Tool thresholds (business rules, kept in one place so they can be tuned) ---
LOW_SAMPLE_THRESHOLD = 10          # below this many reviews, a percentage is flagged as noisy
MIN_PRODUCT_REVIEWS_FOR_TABLE = 3  # minimum reviews for a product to appear in the negative-share table

# --- Excerpt lengths (named separately: these serve different tools) ---
FLAGGED_REVIEW_EXCERPT_CHARS = 400   # around the matched issue term, for flagged_reviews
SEARCH_RESULT_EXCERPT_CHARS = 600    # for search_reviews semantic search results


