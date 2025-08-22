# id_service/core/config.py
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ID Service"
    APP_ENV: str = "development"  # development|production
    ISSUER: str = "http://localhost:8000"
    CORS_ORIGINS: List[str] = []

    # DB / Redis
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/id_service"
    DB_ECHO: bool = False
    REDIS_URL: str = "redis://localhost:6379/1"

    # Security / Secrets
    SECRET_KEY: str = "dev-secret"
    PEPPER_SECRET: str = "dev-pepper"
    COOKIE_SECRET: str = "dev-cookie-secret"
    JWT_PRIVATE_KEY_PASSWORD: str = "dev-jwt-password"

    # Token TTLs (seconds)
    ACCESS_TOKEN_TTL: int = 600
    REFRESH_TOKEN_TTL: int = 2592000
    AUTH_CODE_TTL: int = 600
    SSO_IDLE_TTL: int = 1800
    SSO_MAX_TTL: int = 86400

    # OTP
    OTP_TTL: int = 300
    OTP_RESEND_SECONDS: int = 60
    OTP_MAX_ATTEMPTS: int = 5

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    EMAIL_FROM: str = "Asynq ID <noreply@example.com>"

    # Rate limit
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # Password policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = False

    # Dev client IDs
    TEACH_CLIENT_ID: str = "teach-service"
    RUN_CLIENT_ID: str = "run-service"
    LEARN_CLIENT_ID: str = "learn-service"
    CATALOG_CLIENT_ID: str = "catalog-service"
    ADMIN_CLIENT_ID: str = "admin-service"

    # Argon2id tuning (can be overridden via .env)
    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536  # KiB (64 MiB)
    ARGON2_PARALLELISM: int = 2
    ARGON2_HASH_LEN: int = 32
    ARGON2_SALT_LEN: int = 16

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
