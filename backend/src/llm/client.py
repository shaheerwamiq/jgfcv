"""LLM client factory for Google Gemini via langchain-google-genai.

Centralising model construction means one place to change models,
temperature, retries, or even swap providers (the rest of the codebase
only depends on the LangChain Runnable interface).
"""

from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.config import get_settings


@lru_cache
def get_llm(temperature: float | None = None) -> ChatGoogleGenerativeAI:
    """Build (and cache) a Gemini chat model.

    `lru_cache` keyed on temperature means repeated calls reuse the same
    client and its underlying connection pool.
    """
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature if temperature is None else temperature,
        max_retries=settings.llm_max_retries,
        google_api_key=settings.google_api_key or None,
    )
