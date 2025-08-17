# admin_service/core/config.py
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # v2-стиль, разрешаем лишние переменные и читаем .env
    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True, extra='ignore')

    # DB
    DATABASE_URL: str = "postgresql://postgres:siperup44rQVr8@db:5432/admin_db"

    # Services
    AUTH_SERVICE_URL: str = "http://authservice:8000"
    CATALOG_SERVICE_URL: str = "http://catalogservice:8001"
    LEARNING_SERVICE_URL: str = "http://learningservice:8002"
    POINTS_SERVICE_URL: str = "http://pointsservice:8003"

    # Security
    JWT_SECRET_KEY: str = "pepTkzpoJ20y6gM6EsGVoQe8rFa9OO6PJnnViahsC_RN2W8Cszqe0CmYHIScj-8Wd6Q"
    JWT_ALGORITHM: str = "HS256"
    INTERNAL_TOKEN: str = "4B2pFXFcX33DKQEVofEuv-Wk5SzM0GTWcYTP8PfE4kOVa4oDIwq32gS63VXRvrpm"

    # S3
    S3_ENDPOINT_HOST: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: str = "https://s3.storage.selcloud.ru"
    S3_PUBLIC_BUCKET: str = "course-public"
    S3_PUBLIC_CDN_URL: str = "https://79340a29-0019-4283-b338-388e7f5c1822.selstorage.ru"

    # App
    DEBUG: bool = False
    CORS_ALLOW_ORIGINS: str = "*"

settings = Settings()
