# points_service/api/health.py

"""
Публичный эндпоинт /health для проверки состояния сервиса.
Проверяет доступность БД. Используется для liveness/readiness в оркестраторе.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from points_service.db.dependencies import get_db_session

router = APIRouter()

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db_session)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        detail = {"status": "degraded", "db": "error", "error": str(e)}
        raise HTTPException(status_code=503, detail=detail)
