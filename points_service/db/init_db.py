# points_service/db/init_db.py

"""
Назначение: инициализация БД: движок, сессии, создание таблиц.
Используется: при старте приложения и в init_db.sh.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from urllib.parse import urlparse, urlunparse

from points_service.core.base import Base
from points_service.core.config import settings


def get_async_pg_url(url: str) -> str:
    parsed = urlparse(url)
    if "+asyncpg" in parsed.scheme:
        return url
    return urlunparse(parsed._replace(scheme=parsed.scheme + "+asyncpg"))


DATABASE_URL = get_async_pg_url(settings.DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    # ВАЖНО: импортируем модели перед create_all
    from points_service.models import points as _points_model  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ [points_service] DB schema synced")
