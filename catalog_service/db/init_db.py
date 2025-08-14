# catalog_service/db/init_db.py


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from catalog_service.core.base import Base
from catalog_service.core.config import settings

from urllib.parse import urlparse, urlunparse

def get_async_pg_url(url: str) -> str:
    parsed = urlparse(url)
    if '+asyncpg' in parsed.scheme:
        return url
    async_scheme = parsed.scheme + '+asyncpg'
    return urlunparse(parsed._replace(scheme=async_scheme))

DATABASE_URL = get_async_pg_url(settings.DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    """Создание всех таблиц в БД при старте"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ [DB] Таблицы успешно созданы")
