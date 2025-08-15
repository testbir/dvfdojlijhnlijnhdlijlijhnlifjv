# learning_service/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FASTAPI_ENV: str = "development"
    DATABASE_URL: str
    JWT_SECRET_KEY: str = "fallback-dev-key"

    POINTS_SERVICE_URL: str = "http://pointsservice:8003"
    INTERNAL_TOKEN: str = "change-me"

    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    DEBUG: bool = True

    class Config:
        env_file = "learning_service/.env"

settings = Settings()
