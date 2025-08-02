# catalog_service/api/banner.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.dependencies import get_db_session
from models.banner import Banner
from pydantic import BaseModel
from typing import List, Optional
from schemas.banner import BannerUpdateSchema

router = APIRouter()

class BannerSchema(BaseModel):
    id: int
    image: str
    order: int
    link: str

    class Config:
        orm_mode = True

class BannerCreateSchema(BaseModel):
    image: str
    order: int = 0
    link: Optional[str] = ""

@router.get("/internal/banners/", response_model=List[BannerSchema])
async def list_banners(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Banner).order_by(Banner.order))
    return result.scalars().all()

@router.post("/internal/banners/")
async def create_banner(data: BannerCreateSchema, db: AsyncSession = Depends(get_db_session)):
    banner = Banner(**data.dict())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return {"id": banner.id, "message": "Баннер создан"}

@router.delete("/internal/banners/{banner_id}")
async def delete_banner(banner_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Баннер не найден")
    await db.delete(banner)
    await db.commit()
    return {"message": "Баннер удалён"}

@router.put("/internal/banners/{banner_id}")
async def update_banner(banner_id: int, data: BannerUpdateSchema, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Баннер не найден")

    if data.image is not None:
        banner.image = data.image
    banner.order = data.order
    banner.link = data.link

    await db.commit()
    await db.refresh(banner)
    return banner