# catalog_service/db/dependencies.py

from db.init_db import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session