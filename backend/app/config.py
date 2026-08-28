"""
Centralized configuration using pydantic-settings.
All values are overridable via environment variables / .env file.
This pattern (12-factor config) is a common interview talking point.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "IntelliOps ERP"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://intelliops:intelliops@postgres:5432/intelliops"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL_SECONDS: int = 30  # short TTL to keep dashboard "near real-time"

    # Auth / JWT
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI Agent (pluggable providers)
    LLM_PROVIDER: str = "fallback"  # "openai" | "anthropic" | "fallback"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # gRPC notification service
    GRPC_NOTIFICATION_HOST: str = "grpc_service"
    GRPC_NOTIFICATION_PORT: int = 50051

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
