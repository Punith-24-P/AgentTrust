import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AgentTrust"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database: Supports SQLite (zero-config local) & PostgreSQL (production / Docker)
    DATABASE_URL: str = "sqlite+aiosqlite:///./agenttrust.db"

    # Authentication & Security
    JWT_SECRET: str = "agenttrust-super-secret-key-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    # AI / LLM Layer
    LLM_PROVIDER: str = "mock"  # "mock" | "openai" | "openai_compatible"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"

    # Translation Service
    TRANSLATION_PROVIDER: str = "mock"  # "mock" | "llm"

    # Evaluation Controls
    MAX_CONCURRENCY: int = 4
    EVALUATION_TIMEOUT_SEC: int = 60
    RETRY_COUNT: int = 2

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]

    # Base Paths
    DATA_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
