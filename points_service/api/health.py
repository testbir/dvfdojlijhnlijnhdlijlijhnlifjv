# points_service/api/health.py

"""
Публичный эндпоинт /health для проверки состояния сервиса.
Проверяет доступность БД. Используется для liveness/readiness в оркестраторе.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session

log = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db_session)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        log.exception("Health DB check failed")
        # краткий ответ без секретов
        raise HTTPException(status_code=503, detail={"message": "db_unavailable"})