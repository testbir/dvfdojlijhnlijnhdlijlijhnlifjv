# points_service/db/init_db.py

"""
Назначение: инициализация БД: движок, сессии, создание таблиц.
Используется: при старте приложения и в init_db.sh.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from urllib.parse import urlparse, urlunparse

from points_service.core.config import settings
from points_service.core.base import Base

def get_async_pg_url(url: str) -> str:
    p = urlparse(url)
    if "+asyncpg" in p.scheme:
        return url
    return urlunparse(p._replace(scheme=p.scheme + "+asyncpg"))

DATABASE_URL = get_async_pg_url(settings.DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    from points_service.models import points as _points  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
