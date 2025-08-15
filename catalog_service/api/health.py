#catalog_service/health.py

from fastapi import APIRouter
router = APIRouter()
@router.get("/health")
async def health(): return {"ok": True}
