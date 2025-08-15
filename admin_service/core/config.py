# admin_service/core/config.py

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:siperup44rQVr8@db:5432/admin_db"
    )
    
    # Service URLs
    AUTH_SERVICE_URL: str = os.getenv(
        "AUTH_SERVICE_URL",
        "http://authservice:8002"
    )
    CATALOG_SERVICE_URL: str = os.getenv(
        "CATALOG_SERVICE_URL", 
        "http://catalogservice:8001"
    )
    LEARNING_SERVICE_URL: str = os.getenv(
        "LEARNING_SERVICE_URL",
        "http://learningservice:8002"
    )
    POINTS_SERVICE_URL: str = os.getenv(
        "POINTS_SERVICE_URL",
        "http://pointsservice:8003"
    )
    
    # Security
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "pepTkzpoJ20y6gM6EsGVoQe8rFa9OO6PJnnViahsC_RN2W8Cszqe0CmYHIScj-8Wd6Q"
    )
    JWT_ALGORITHM: str = "HS256"
    INTERNAL_TOKEN: str = os.getenv(
        "INTERNAL_TOKEN",
        "4B2pFXFcX33DKQEVofEuv-Wk5SzM0GTWcYTP8PfE4kOVa4oDIwq32gS63VXRvrpm"
    )
    
    # S3 Storage
    S3_ACCESS_KEY: Optional[str] = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = os.getenv("S3_SECRET_KEY")
    S3_ENDPOINT_URL: str = os.getenv(
        "S3_ENDPOINT_URL",
        "https://s3.storage.selcloud.ru"
    )
    S3_BUCKET_NAME: str = os.getenv(
        "S3_BUCKET_NAME",
        "course-public"
    )
    S3_PUBLIC_URL: str = os.getenv(
        "S3_PUBLIC_URL",
        "https://79340a29-0019-4283-b338-388e7f5c1822.selstorage.ru"
    )
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    CORS_ALLOW_ORIGINS: str = os.getenv("CORS_ALLOW_ORIGINS", "*")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()