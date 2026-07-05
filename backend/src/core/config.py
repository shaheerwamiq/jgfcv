"""Application configuration via pydantic-settings.

Every tunable lives here so behaviour can be changed without code edits.
Values are read from environment variables (and .env files in development).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central, validated application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- LLM ---
    google_api_key: str = ""
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.3
    llm_max_retries: int = 3
    embedding_model: str = "models/gemini-embedding-001"

    # --- RAG ---
    chunk_size: int = 800
    chunk_overlap: int = 120
    retriever_k: int = 4

    # --- Guardrails ---
    guardrails_enabled: bool = True
    max_input_chars: int = 8000

    # --- Cache ---
    cache_ttl_seconds: int = 300

    # --- App ---
    app_name: str = "AgentForge"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (import this, not Settings directly)."""
    return Settings()
