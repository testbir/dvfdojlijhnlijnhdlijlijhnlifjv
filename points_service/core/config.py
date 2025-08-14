# points_service/core/config.py

"""
Назначение: глобальные настройки сервиса (env, токены, лимиты, БД).
Используется: во всех модулях для доступа к переменным окружения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FASTAPI_ENV: str = "development"

    DATABASE_URL: str

    # JWT для публичных запросов (декодируем user_id)
    JWT_SECRET_KEY: str = "dev-secret"
    JWT_ALGORITHM: str = "HS256"

    # Токен для внутренних/админских запросов (Bearer)
    INTERNAL_TOKEN: str = "change-me"

    # Логи SQL
    DEBUG: bool = False

    # CORS
    CORS_ALLOW_ORIGINS: str = "*"  # через запятую если нужно ограничить

    class Config:
        env_file = "points_service/.env"


settings = Settings()
