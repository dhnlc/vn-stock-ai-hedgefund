"""Application settings loaded from environment and .env file.

Uses pydantic-settings to parse environment variables and optional `.env`.
"""

from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Model/provider configuration
    AGNO_MODEL_PROVIDER: Literal["openai", "anthropic", "groq"] = "openai"
    AGNO_MODEL_ID: Optional[str] = None
    AGNO_API_ENABLED: bool = False

    # API keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Data sources
    DATA_SOURCE: Literal["yfinance", "vnstock"] = "yfinance"
    VNSTOCK_SOURCE: Literal["VCI", "TCBS", "MSN"] = "VCI"


# Singleton settings instance
settings = Settings()  # type: ignore[call-arg]
