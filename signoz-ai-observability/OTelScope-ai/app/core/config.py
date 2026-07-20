"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values for OTelScope AI."""

    app_name: str = "OTelScope AI"
    app_service_name: str = "otelscope-ai-api"
    app_version: str = "0.1.0"
    app_environment: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8001

    llm_provider: str = "simulated"
    llm_model: str = "demo-model"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""

    return Settings()
