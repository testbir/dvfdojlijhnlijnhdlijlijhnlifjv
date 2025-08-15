#admin_service/core/config.py

from pydantic_settings import BaseSettings
from typing import Optional, Set

class Settings(BaseSettings):
    # Runtime
    FASTAPI_ENV: str = "production"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: Optional[str] = None
    JWT_AUDIENCE: Optional[str] = None
    JWT_LEEWAY_SECONDS: int = 60
    ADMIN_ALLOWED_ROLES: Set[str] = {"admin", "superadmin"}

    # External services
    CATALOG_SERVICE_URL: str = "http://catalogservice:8001"
    LEARNING_SERVICE_URL: str = "http://learningservice:8002"
    INTERNAL_TOKEN: str

    # Database
    DATABASE_URL: str
    REDIS_URL: Optional[str] = None

    # S3 (как было, без изменений)
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ENDPOINT_HOST: Optional[str] = None
    S3_PUBLIC_BUCKET: Optional[str] = None
    S3_CONTENT_BUCKET: Optional[str] = None
    S3_PUBLIC_CDN_URL: Optional[str] = None
    S3_CONTENT_CDN_URL: Optional[str] = None

    class Config:
        env_file = "admin_service/.env"

settings = Settings()
