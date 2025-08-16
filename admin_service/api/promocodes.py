# admin_service/api/promocodes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import httpx
from pydantic import BaseModel
from core.config import settings
from utils.auth import get_current_admin_user
from models.admin import AdminUser

router = APIRouter(prefix="/admin/promocodes", tags=["Admin Promocodes"])

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL
def _hdr(): return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

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

@router.get("/")
async def list_promocodes(current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.get("/v1/admin/promocodes", headers=_hdr())
        r.raise_for_status(); return r.json()

@router.post("/")
async def create_promocode(data: PromoCodeCreate, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.post("/v1/admin/promocodes", headers=_hdr(), json=data.model_dump())
        if r.status_code == 400:
            raise HTTPException(status_code=400, detail="Промокод уже существует")
        r.raise_for_status(); return r.json()

@router.put("/{promo_id}")
async def update_promocode(promo_id: int, data: PromoCodeUpdate, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.put(f"/v1/admin/promocodes/{promo_id}", headers=_hdr(), json=data.model_dump(exclude_unset=True))
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Промокод не найден")
        r.raise_for_status(); return r.json()

@router.delete("/{promo_id}")
async def delete_promocode(promo_id: int, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.delete(f"/v1/admin/promocodes/{promo_id}", headers=_hdr())
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Промокод не найден")
        r.raise_for_status(); return {"success": True}

@router.post("/{promo_id}/toggle-active/")
async def toggle_promocode_active(promo_id: int, is_active: bool, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.put(f"/v1/admin/promocodes/{promo_id}", headers=_hdr(), json={"is_active": is_active})
        r.raise_for_status(); return {"success": True, "is_active": is_active}

@router.get("/statistics/")
async def get_promocode_statistics(current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.get("/v1/admin/promocodes", headers=_hdr())
        r.raise_for_status()
        promocodes = r.json()
    total = len(promocodes)
    active = sum(1 for p in promocodes if p.get("is_active"))
    total_uses = sum(max(0, p.get("max_uses", 0) - p.get("uses_left", 0)) for p in promocodes)
    return {"total_promocodes": total, "active_promocodes": active, "total_uses": total_uses, "promocodes": promocodes}
