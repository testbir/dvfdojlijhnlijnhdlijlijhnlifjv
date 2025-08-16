# catalog_service/api/admin/promocodes.py

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from db.dependencies import get_db_session
from models.promocode import PromoCode


router = APIRouter(prefix="/promocodes")

class PromoCodeCreate(BaseModel):
    code: str
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    max_uses: int = 100
    valid_from: datetime
    valid_until: datetime
    applicable_courses: List[int] = Field(default_factory=list)

class PromoCodeUpdate(BaseModel):
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    max_uses: Optional[int] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None

class PromoCodeResponse(BaseModel):
    id: int
    code: str
    discount_percent: Optional[float]
    discount_amount: Optional[float]
    uses_left: int
    max_uses: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    applicable_courses: List[int]

    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=List[PromoCodeResponse])
async def list_promocodes(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(PromoCode))
    return result.scalars().all()

@router.post("/", response_model=PromoCodeResponse)
async def create_promocode(data: PromoCodeCreate, db: AsyncSession = Depends(get_db_session)):
    # Проверяем уникальность кода
    result = await db.execute(
        select(PromoCode).where(PromoCode.code == data.code)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Промокод с таким кодом уже существует")

    if not data.discount_percent and not data.discount_amount:
        raise HTTPException(status_code=400, detail="Укажите размер скидки")

    if data.discount_percent and data.discount_amount:
        raise HTTPException(status_code=400, detail="Нельзя использовать обе скидки одновременно")

    if data.valid_until < data.valid_from:
        raise HTTPException(status_code=400, detail="Дата окончания не может быть раньше даты начала")

    # 🔧 Удаляем tzinfo, чтобы привести к naive datetime
    valid_from = data.valid_from.replace(tzinfo=None)
    valid_until = data.valid_until.replace(tzinfo=None)

    promo = PromoCode(
        code=data.code,
        discount_percent=data.discount_percent,
        discount_amount=data.discount_amount,
        uses_left=data.max_uses,
        max_uses=data.max_uses,
        valid_from=valid_from,
        valid_until=valid_until,
        is_active=True,
        applicable_courses=data.applicable_courses,
    )
    db.add(promo)
    await db.commit()
    await db.refresh(promo)
    return promo

@router.put("/{promo_id}", response_model=PromoCodeResponse)
async def update_promocode(promo_id: int, data: PromoCodeUpdate, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(PromoCode).where(PromoCode.id == promo_id))
    promo = result.scalar_one_or_none()
    if not promo:
        raise HTTPException(status_code=404, detail="Промокод не найден")

    updates = data.model_dump(exclude_unset=True)
    if "valid_until" in updates and updates["valid_until"] is not None:
        updates["valid_until"] = updates["valid_until"].replace(tzinfo=None)

    for key, value in updates.items():
        setattr(promo, key, value)

    await db.commit()
    await db.refresh(promo)
    return promo


@router.delete("/{promo_id}")
async def delete_promocode(promo_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(PromoCode).where(PromoCode.id == promo_id)
    )
    promo = result.scalar_one_or_none()
    if not promo:
        raise HTTPException(status_code=404, detail="Промокод не найден")

    await db.delete(promo)
    await db.commit()
    return Response(status_code=204)

