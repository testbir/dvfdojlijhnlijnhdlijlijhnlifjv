# admin_service/api/promocodes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import httpx
from utils.auth import get_current_user
from core.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/admin/promocodes", tags=["Admin Promocodes"])

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL

class PromoCodeCreate(BaseModel):
    code: str
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    max_uses: int = 100
    valid_from: datetime
    valid_until: datetime
    applicable_courses: List[int] = []

class PromoCodeUpdate(BaseModel):
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    max_uses: Optional[int] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None

@router.get("/", summary="Получить список промокодов")
async def list_promocodes(user_id: str = Depends(get_current_user)):
    """Получает список всех промокодов"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CATALOG_SERVICE_URL}/promocodes/internal/")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.post("/", summary="Создать промокод")
async def create_promocode(
    data: PromoCodeCreate,
    user_id: str = Depends(get_current_user)
):
    """Создает новый промокод"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CATALOG_SERVICE_URL}/promocodes/internal/",
                content=data.json(),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise HTTPException(status_code=400, detail="Промокод с таким кодом уже существует")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.put("/{promo_id}", summary="Обновить промокод")
async def update_promocode(
    promo_id: int,
    data: PromoCodeUpdate,
    user_id: str = Depends(get_current_user)
):
    """Обновляет существующий промокод"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CATALOG_SERVICE_URL}/promocodes/internal/{promo_id}",
                json=data.dict(exclude_unset=True)
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Промокод не найден")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.delete("/{promo_id}", summary="Удалить промокод")
async def delete_promocode(
    promo_id: int,
    user_id: str = Depends(get_current_user)
):
    """Удаляет промокод"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CATALOG_SERVICE_URL}/promocodes/internal/{promo_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Промокод не найден")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.post("/{promo_id}/toggle-active/", summary="Активировать/деактивировать промокод")
async def toggle_promocode_active(
    promo_id: int,
    is_active: bool,
    user_id: str = Depends(get_current_user)
):
    """Изменяет статус активности промокода"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CATALOG_SERVICE_URL}/promocodes/internal/{promo_id}",
                json={"is_active": is_active}
            )
            response.raise_for_status()
            return {"success": True, "is_active": is_active}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.get("/statistics/", summary="Статистика использования промокодов")
async def get_promocode_statistics(user_id: str = Depends(get_current_user)):
    """Получает статистику использования промокодов"""
    try:
        async with httpx.AsyncClient() as client:
            # Получаем все промокоды
            response = await client.get(f"{CATALOG_SERVICE_URL}/promocodes/internal/")
            response.raise_for_status()
            promocodes = response.json()
            
            # Считаем статистику
            total = len(promocodes)
            active = sum(1 for p in promocodes if p['is_active'])
            total_uses = sum(p['max_uses'] - p['uses_left'] for p in promocodes)
            
            return {
                "total_promocodes": total,
                "active_promocodes": active,
                "total_uses": total_uses,
                "promocodes": promocodes
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))