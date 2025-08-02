# catalog_service/db/init_db.py


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.base import Base
from core.config import settings

DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    """Создание всех таблиц в БД при старте"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ [DB] Таблицы успешно созданы")
