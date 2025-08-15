# learning_service/db/tx.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

async def commit_or_rollback(db: AsyncSession):
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
