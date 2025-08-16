# catalog_service/api/admin/banner.py

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from schemas.banner import BannerSchema, BannerCreateSchema, BannerUpdateSchema
from db.dependencies import get_db_session
from models.banner import Banner

router = APIRouter(prefix="/banners")

@router.get("/", response_model=List[BannerSchema])
async def list_banners(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Banner).order_by(Banner.order))
    return result.scalars().all()

@router.post("/")
async def create_banner(data: BannerCreateSchema, db: AsyncSession = Depends(get_db_session)):
    banner = Banner(**data.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return {"id": banner.id, "message": "Баннер создан"}

@router.delete("/{banner_id}")
async def delete_banner(banner_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Баннер не найден")
    await db.delete(banner)
    await db.commit()
    return Response(status_code=204)

@router.put("/{banner_id}", response_model=BannerSchema)
async def update_banner(banner_id: int, data: BannerUpdateSchema, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Баннер не найден")

    # защищаем NOT NULL для image
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "image" and v is None:
            continue
        setattr(banner, k, v)

    await db.commit()
    await db.refresh(banner)
    return banner
