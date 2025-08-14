# catalog_service/api/admin/promo.py

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from catalog_service.db.dependencies import get_db_session
from catalog_service.models.promo import PromoImage
from catalog_service.schemas.promo import PromoSchema, PromoCreateSchema

from typing import List

router = APIRouter(prefix="/promos")

@router.get("/", response_model=List[PromoSchema])
async def list_promos(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(PromoImage).order_by(PromoImage.order)
    )
    return result.scalars().all()

@router.post("/")
async def create_promo(data: PromoCreateSchema, db: AsyncSession = Depends(get_db_session)):
    promo = PromoImage(**data.model_dump())
    db.add(promo)
    await db.commit()
    await db.refresh(promo)
    return {"id": promo.id, "message": "Промо добавлено"}

@router.delete("/{promo_id}")
async def delete_promo(promo_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(PromoImage).where(PromoImage.id == promo_id))
    promo = result.scalar_one_or_none()
    if not promo:
        raise HTTPException(status_code=404, detail="Промо не найдено")
    await db.delete(promo)
    await db.commit()
    return Response(status_code=204)