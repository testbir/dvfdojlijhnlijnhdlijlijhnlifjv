
# catalog_service/scripts/init_db_async.py



import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from core.base import Base
from core.config import settings

from models.course import Course
from models.module import Module
from models.content import ContentBlock
from models.access import CourseAccess
from models.progress import UserModuleProgress
from models.banner import Banner
from models.promo import PromoImage

DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(DATABASE_URL, echo=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
