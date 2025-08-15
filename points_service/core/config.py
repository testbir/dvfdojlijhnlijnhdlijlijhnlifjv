# points_service/core/config.py

"""
Назначение: глобальные настройки сервиса (env, токены, лимиты, БД).
Используется: во всех модулях для доступа к переменным окружения.
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    FASTAPI_ENV: str = "development"
    DATABASE_URL: str

    JWT_SECRET_KEY: str = "dev-secret"
    JWT_ALGORITHM: str = "HS256"

    INTERNAL_TOKEN: str = "change-me"

    DEBUG: bool = False
    CORS_ALLOW_ORIGINS: str = "*"  # comma-separated

    class Config:
        env_file = "points_service/.env"

    @property
    def cors_origins(self) -> List[str]:
        raw = (self.CORS_ALLOW_ORIGINS or "").strip()
        return ["*"] if raw in {"", "*"} else [o.strip() for o in raw.split(",")]

settings = Settings()
