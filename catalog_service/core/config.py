# catalog_service/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FASTAPI_ENV: str = "development"

    DATABASE_URL: str

    JWT_SECRET_KEY: str = "fallback-dev-key"

    GLOBAL_RATE_LIMIT: str = "30/2minute"
    BUY_COURSE_RATE_LIMIT: str = "3/minute"
    COMPLETE_MODULE_RATE_LIMIT: str = "10/minute"
    
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Отслеживание SQL
    
    DEBUG: bool = True

    class Config:
        env_file = "catalog_service/.env"


settings = Settings()