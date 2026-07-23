"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed configuration for OTelScope AI."""

    # Application
    app_name: str = "OTelScope AI"
    app_service_name: str = "otelscope-ai-api"
    app_environment: str = "development"
    app_version: str = "0.1.0"

    app_host: str = "127.0.0.1"
    app_port: int = Field(
        default=8001,
        ge=1,
        le=65535,
    )

    # LLM
    llm_provider: str = "simulated"
    llm_model: str = "demo-model"
    llm_api_key: str | None = None

    # Simulated pricing used only for learning and metric generation
    llm_input_cost_per_1k_tokens: float = 0.001
    llm_output_cost_per_1k_tokens: float = 0.002    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()