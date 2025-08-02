#admin_service/core/config.py

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    CATALOG_SERVICE_URL: str = "http://catalogservice:8001"

    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_ENDPOINT_URL: str
    S3_PUBLIC_CDN_URL: str
    S3_CONTENT_CDN_URL: str
    S3_ENDPOINT_HOST: str
    S3_PUBLIC_BUCKET: str
    S3_CONTENT_BUCKET: str
    S3_DEFAULT_BUCKET: str = "public"

    model_config = ConfigDict(env_file=".env", extra="allow")


settings = Settings()
