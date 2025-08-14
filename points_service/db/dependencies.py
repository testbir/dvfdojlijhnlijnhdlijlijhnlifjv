# points_service/db/dependencies.py

"""
Назначение: зависимость FastAPI для получения async-сессии БД.
Используется: в хэндлерах.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from points_service.db.init_db import async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
