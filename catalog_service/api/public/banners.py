# catalog_service/api/public/banners.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from db.dependencies import get_db_session
from models.banner import Banner
from schemas.banner import BannerSchema

router = APIRouter(prefix="/banners", tags=["Public - Banners"])

@router.get("/", response_model=List[BannerSchema], summary="Публичные баннеры")
async def list_public_banners(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Banner).order_by(Banner.order.asc()))
    return res.scalars().all()
