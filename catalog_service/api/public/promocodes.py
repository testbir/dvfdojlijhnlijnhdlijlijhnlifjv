# catalog_service/api/public/promocodes.py

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from db.dependencies import get_db_session
from models.promocode import PromoCode

router = APIRouter(prefix="/promocodes")

@router.post("/check/")
async def check_promocode(
    code: str = Body(..., embed=True),
    course_id: Optional[int] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(select(PromoCode).where(PromoCode.code == code, PromoCode.is_active == True))
    promo = result.scalar_one_or_none()
    if not promo:
        raise HTTPException(status_code=404, detail="Промокод не найден или неактивен")
    now = datetime.utcnow()
    if now < promo.valid_from or now > promo.valid_until:
        raise HTTPException(status_code=400, detail="Срок действия промокода истек")
    if promo.uses_left <= 0:
        raise HTTPException(status_code=400, detail="Промокод больше не может быть использован")
    if course_id and promo.applicable_courses and course_id not in promo.applicable_courses:
        raise HTTPException(status_code=400, detail="Промокод не применим к данному курсу")
    return {"valid": True, "discount_percent": promo.discount_percent, "discount_amount": promo.discount_amount}

@router.post("/use/")
async def use_promocode(
    code: str = Body(..., embed=True),
    course_id: Optional[int] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db_session),
):

    async with db.begin():  # открываем транзакцию
        result = await db.execute(
            select(PromoCode)
            .where(PromoCode.code == code, PromoCode.is_active == True)
            .with_for_update()  # 🔒 блокируем строку до конца транзакции
        )
        promo = result.scalar_one_or_none()
        if not promo:
            raise HTTPException(status_code=404, detail="Промокод не найден")

        now = datetime.utcnow()
        if now < promo.valid_from or now > promo.valid_until:
            raise HTTPException(status_code=400, detail="Срок действия промокода истек")

        if course_id and promo.applicable_courses and course_id not in promo.applicable_courses:
            raise HTTPException(status_code=400, detail="Промокод не применим к данному курсу")

        if promo.uses_left <= 0:
            raise HTTPException(status_code=400, detail="Промокод больше не может быть использован")

        promo.uses_left -= 1
        # commit произойдёт автоматически при выходе из async with

    return {
        "success": True,
        "discount_percent": promo.discount_percent,
        "discount_amount": promo.discount_amount
    }