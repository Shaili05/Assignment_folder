import logging
import os
import time

from src.config.constants import (
    LLM_FATAL_STATUS_CODES, LLM_MAX_RETRIES, LLM_MAX_TOKENS, LLM_RETRY_BACKOFF_SEC, LLM_TEMPERATURE, RATE_LIMIT_STATUS_CODE
)

from src.exceptions.exceptions import ConfigurationError, LLMProviderError, RateLimitError

logger = logging.getLogger(__name__)

_state = {}


def get_client():
    if "client" not in _state:
        from groq import Groq

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ConfigurationError("GROQ_API_KEY not found in .env")
        _state["client"] = Groq(api_key=api_key)
    return _state["client"]


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
    if last_status == RATE_LIMIT_STATUS_CODE:
        raise RateLimitError()
    raise LLMProviderError("The language model did not respond after several retries.")
