# admin_service/api/banners.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
import httpx
from core.config import settings
from utils.auth import get_current_admin_user
from models.admin import AdminUser
import logging

router = APIRouter(prefix="/admin/banners", tags=["Admin Banners"])
logger = logging.getLogger(__name__)

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL

def _hdr():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

@router.get("/", response_model=List[dict])
async def get_banners(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить список всех баннеров"""
    logger.info(f"Admin {current_admin.username} fetching banners list")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.get("/v1/admin/banners/", headers=_hdr())
        response.raise_for_status()
        return response.json()

@router.get("/{banner_id}", response_model=dict)
async def get_banner(
    banner_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить баннер по ID"""
    logger.info(f"Admin {current_admin.username} fetching banner {banner_id}")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(f"/v1/admin/banners/{banner_id}", headers=_hdr())
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Баннер не найден")
        response.raise_for_status()
        return response.json()

@router.post("/", response_model=dict)
async def create_banner(
    image: str = Body(...),
    order: int = Body(0),
    link: Optional[str] = Body(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создать новый баннер"""
    logger.info(f"Admin {current_admin.username} creating new banner")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.post(
            "/v1/admin/banners/",
            headers=_hdr(),
            json={"image": image, "order": order, "link": link}
        )
        response.raise_for_status()
        return response.json()

@router.put("/{banner_id}", response_model=dict)
async def update_banner(
    banner_id: int,
    image: Optional[str] = Body(None),
    order: Optional[int] = Body(None),
    link: Optional[str] = Body(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновить существующий баннер"""
    logger.info(f"Admin {current_admin.username} updating banner {banner_id}")
    
    data = {}
    if image is not None:
        data["image"] = image
    if order is not None:
        data["order"] = order
    if link is not None:
        data["link"] = link
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.put(
            f"/v1/admin/banners/{banner_id}",
            headers=_hdr(),
            json=data
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Баннер не найден")
        response.raise_for_status()
        return response.json()

@router.delete("/{banner_id}")
async def delete_banner(
    banner_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удалить баннер"""
    logger.warning(f"Admin {current_admin.username} deleting banner {banner_id}")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.delete(
            f"/v1/admin/banners/{banner_id}",
            headers=_hdr()
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Баннер не найден")
        response.raise_for_status()
        return {"message": "Баннер успешно удален"}

@router.post("/reorder")
async def reorder_banners(
    order_map: dict = Body(...),  # {banner_id: new_order}
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Изменить порядок отображения баннеров"""
    logger.info(f"Admin {current_admin.username} reordering banners")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        # Обновляем порядок для каждого баннера
        for banner_id, new_order in order_map.items():
            response = await client.put(
                f"/v1/admin/banners/{banner_id}",
                headers=_hdr(),
                json={"order": new_order}
            )
            response.raise_for_status()
        
        return {"message": "Порядок баннеров обновлен"}