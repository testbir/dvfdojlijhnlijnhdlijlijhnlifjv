# admin_service/api/modules.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, List
import httpx
from core.config import settings
from utils.auth import get_current_admin_user
from models.admin import AdminUser
import logging

router = APIRouter(tags=["Admin - Modules"])
logger = logging.getLogger(__name__)

LEARNING_SERVICE_URL = settings.LEARNING_SERVICE_URL

def _hdr():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

# ИСПРАВЛЕНО: убрали слеш в конце URL
@router.get("/admin/courses/{course_id}/modules")
async def get_course_modules(
    course_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить все модули курса"""
    logger.info(f"Admin {current_admin.username} fetching modules for course {course_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(
            f"/v1/admin/courses/{course_id}/modules/",  # оставляем слеш для learning_service
            headers=_hdr()
        )
        response.raise_for_status()
        return response.json()

# ИСПРАВЛЕНО: убрали слеш в конце URL
@router.post("/admin/courses/{course_id}/modules")
async def create_module(
    course_id: int,
    title: str = Body(...),
    group_title: Optional[str] = Body(None),
    order: Optional[int] = Body(None),
    sp_award: Optional[int] = Body(0),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создать новый модуль в курсе"""
    logger.info(f"Admin {current_admin.username} creating module in course {course_id}")
    
    payload = {
        "title": title,
        "group_title": group_title,
        "order": order,
        "sp_award": sp_award
    }
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.post(
            f"/v1/admin/courses/{course_id}/modules/",  # оставляем слеш для learning_service
            headers=_hdr(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

@router.get("/admin/modules/{module_id}")
async def get_module(
    module_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить информацию о модуле"""
    logger.info(f"Admin {current_admin.username} fetching module {module_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(
            f"/v1/admin/modules/{module_id}",
            headers=_hdr()
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Модуль не найден")
        response.raise_for_status()
        return response.json()

@router.put("/admin/modules/{module_id}")
async def update_module(
    module_id: int,
    title: Optional[str] = Body(None),
    group_title: Optional[str] = Body(None),
    order: Optional[int] = Body(None),
    sp_award: Optional[int] = Body(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновить модуль"""
    logger.info(f"Admin {current_admin.username} updating module {module_id}")
    
    payload = {}
    if title is not None:
        payload["title"] = title
    if group_title is not None:
        payload["group_title"] = group_title
    if order is not None:
        payload["order"] = order
    if sp_award is not None:
        payload["sp_award"] = sp_award
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.put(
            f"/v1/admin/modules/{module_id}",
            headers=_hdr(),
            json=payload
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Модуль не найден")
        response.raise_for_status()
        return response.json()

@router.delete("/admin/modules/{module_id}")
async def delete_module(
    module_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удалить модуль"""
    logger.warning(f"Admin {current_admin.username} deleting module {module_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.delete(
            f"/v1/admin/modules/{module_id}",
            headers=_hdr()
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Модуль не найден")
        response.raise_for_status()
        return {"success": True, "message": "Модуль удален"}