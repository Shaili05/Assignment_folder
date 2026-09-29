"""
generator.py

Grounded answer generation from retrieved reviews.

The prompt tells the model to answer only from the numbered excerpts, to cite
review ids like [R123], and to treat excerpt text as untrusted data. After
generation, citations and quoted phrases are checked against the excerpts.
"""

import logging
import os
import time

from src.config.constants import (
    LLM_FATAL_STATUS_CODES, LLM_MAX_RETRIES, LLM_MAX_TOKENS, LLM_RETRY_BACKOFF_SEC, LLM_TEMPERATURE,
)
from src.config.prompts import GENERATOR_SYSTEM_PROMPT
from src.config.settings import LLM_MODEL
from src.exceptions.exceptions import ConfigurationError, LLMProviderError, RateLimitError
from src.guardrails.grounding import CITATION_REGEX, unsupported_quotes

logger = logging.getLogger(__name__)

RATE_LIMIT_STATUS = 429

_state = {}


def get_client():
    if "client" not in _state:
        from groq import Groq

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ConfigurationError("GROQ_API_KEY not found in .env")
        _state["client"] = Groq(api_key=api_key)
    return _state["client"]


def build_context(reviews):
    lines = []
    for r in reviews:
        text = " ".join(str(r["review_text"]).split()).replace("<", "(").replace(">", ")")
        lines.append(f'<review id="R{r["review_id"]}" rating="{r["rating"]}" date="{r["submission_date"]}">{text}</review>')
    return "\n".join(lines)


def call_llm(messages, model):
    client = get_client()
    last_status = None
    for attempt in range(LLM_MAX_RETRIES):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
            )
        except Exception as exc:
            last_status = getattr(exc, "status_code", None)
            if last_status in LLM_FATAL_STATUS_CODES:
                logger.error("LLM request rejected (%s): %s", exc.__class__.__name__, exc)
                raise LLMProviderError(
                    f"The language model request was rejected ({exc.__class__.__name__})."
                ) from exc
            if attempt == LLM_MAX_RETRIES - 1:
                logger.error("LLM call failed on the last attempt: %s", exc)
                break
            wait = LLM_RETRY_BACKOFF_SEC * (2 ** attempt)
            logger.warning(
                "LLM call failed (attempt %d of %d): %s. Retrying in %d seconds.",
                attempt + 1, LLM_MAX_RETRIES, exc, wait,
            )
            time.sleep(wait)
    if last_status == RATE_LIMIT_STATUS:
        raise RateLimitError()
    raise LLMProviderError("The language model did not respond after several retries.")


def generate_answer(question, reviews, model=None):
    model = model or LLM_MODEL
    if not reviews:
        return {
            "answer": "No reviews matched the question and filters.",
            "citations": [], "invalid_citations": [], "unsupported_quotes": [],
            "injection_detected": False, "model": model,
            "latency_sec": 0.0, "prompt_tokens": 0, "completion_tokens": 0,
        }

    user_message = f"Question: {question}\n\nReview excerpts:\n{build_context(reviews)}"
    messages = [
        {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    started = time.time()
    response = call_llm(messages, model)
    latency = round(time.time() - started, 2)

    answer = (response.choices[0].message.content or "").strip()
    if not answer:
        answer = "The model returned an empty response. Please try again."

    retrieved_ids = {int(r["review_id"]) for r in reviews}
    cited = []
    for match in CITATION_REGEX.findall(answer):
        if int(match) not in cited:
            cited.append(int(match))

    usage = response.usage
    return {
        "answer": answer,
        "citations": [c for c in cited if c in retrieved_ids],
        "invalid_citations": [c for c in cited if c not in retrieved_ids],
        "unsupported_quotes": unsupported_quotes(answer, reviews),
        "injection_detected": any(r.get("instruction_like") for r in reviews),
        "model": model,
        "latency_sec": latency,
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
        "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
    }


