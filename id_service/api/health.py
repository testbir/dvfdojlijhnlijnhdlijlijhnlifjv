# id_service/api/health.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.session import get_async_session
from utils.rate_limit import rate_limiter

from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "id-service"
    }


@router.get("/health/ready")
async def readiness(session: AsyncSession = Depends(get_async_session)):
    """Readiness check with database connection"""
    try:
        # Check database
        await session.execute(text("SELECT 1"))
        
        # Check Redis
        redis_healthy = False
        if rate_limiter.redis_client:
            try:
                await rate_limiter.redis_client.ping()
                redis_healthy = True
            except:
                pass
        
        return {
            "status": "ready",
            "database": "connected",
            "redis": "connected" if redis_healthy else "disconnected"
        }
    except Exception as e:
        return JSONResponse(
            {"status": "not_ready", "error": str(e)},
            status_code=503
        )