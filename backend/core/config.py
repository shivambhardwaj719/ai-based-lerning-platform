"""
Central configuration management using Pydantic Settings.
All settings are read from environment variables (or .env file).

Convention used here:
  - No default  →  required; the app will refuse to start if missing.
  - Optional[str] = None  →  optional integration; feature disabled when absent.
  - Scalar default  →  non-sensitive tuning knob (timeouts, pool sizes, flags).
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_NAME: str = "AI Learning Platform"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = False
    APP_SECRET_KEY: str = Field(min_length=32)          # required — no default
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str                                    # required — no default
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str                                       # required — no default
    REDIS_CACHE_TTL: int = 3600
    REDIS_SESSION_TTL: int = 86400
    REDIS_MAX_CONNECTIONS: int = 100

    # ── Kafka ─────────────────────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str                        # required — no default
    KAFKA_CONSUMER_GROUP: str = "ai-learning-platform"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"

    # ── Elasticsearch ─────────────────────────────────────────────────────────
    ELASTICSEARCH_URL: str                              # required — no default
    ELASTICSEARCH_USERNAME: str = "elastic"
    ELASTICSEARCH_PASSWORD: Optional[str] = None        # None = no auth (ES security disabled)
    ELASTICSEARCH_INDEX_PREFIX: str = "ai_learning"

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_SECRET_KEY: str = Field(min_length=32)          # required — no default

    # ── 2FA ───────────────────────────────────────────────────────────────────
    TOTP_ISSUER: str = "AI Learning Platform"

    # ── OAuth Providers (all optional — None disables the provider) ───────────
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = None

    DISCORD_CLIENT_ID: Optional[str] = None
    DISCORD_CLIENT_SECRET: Optional[str] = None
    DISCORD_REDIRECT_URI: Optional[str] = None

    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: Optional[str] = None

    META_CLIENT_ID: Optional[str] = None
    META_CLIENT_SECRET: Optional[str] = None
    META_REDIRECT_URI: Optional[str] = None

    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None                     # None disables email sending
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@ailearning.com"
    SMTP_FROM_NAME: str = "AI Learning Platform"
    SMTP_TLS: bool = True

    # ── AI APIs ───────────────────────────────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    DEFAULT_AI_MODEL: str = "gpt-4o-mini"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── Vector Database ───────────────────────────────────────────────────────
    QDRANT_URL: str                                      # required — no default
    QDRANT_API_KEY: Optional[str] = None

    # ── AWS S3 ────────────────────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None
    CDN_URL: Optional[str] = None

    # ── Payments ──────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str                               # required — no default
    CELERY_RESULT_BACKEND: str                           # required — no default

    # ── Code Execution ────────────────────────────────────────────────────────
    CODE_EXECUTION_TIMEOUT: int = 30
    CODE_EXECUTION_MEMORY_LIMIT_MB: int = 256
    CODE_EXECUTION_CPU_QUOTA: int = 50000

    # ── Monitoring ────────────────────────────────────────────────────────────
    PROMETHEUS_ENABLED: bool = True
    JAEGER_HOST: str = "jaeger"
    JAEGER_PORT: int = 6831
    SENTRY_DSN: Optional[str] = None

    # ── Security ──────────────────────────────────────────────────────────────
    ENCRYPTION_KEY: Optional[str] = None                # None disables field encryption
    PASSWORD_HASH_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # ── Feature Flags ─────────────────────────────────────────────────────────
    FEATURE_AI_MENTOR: bool = True
    FEATURE_CONTESTS: bool = True
    FEATURE_DEVOPS_LABS: bool = True
    FEATURE_AI_PLAYGROUND: bool = True

    @field_validator("APP_SECRET_KEY", "JWT_SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_keys(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("Secret keys must be at least 32 characters")
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
