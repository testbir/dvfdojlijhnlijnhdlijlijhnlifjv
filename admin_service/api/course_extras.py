# admin_service/api/course_extras.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional, Dict, Any
import httpx
from admin_service.core.config import settings
from admin_service.utils.auth import get_current_admin_user
from admin_service.models.admin import AdminUser
import logging

router = APIRouter(prefix="/admin/course-extras", tags=["Course Extras"])
logger = logging.getLogger(__name__)

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL
def _hdr(): 
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

# === МОДАЛЬНЫЕ ОКНА ===
@router.get("/modal/{course_id}/")
async def get_course_modal(
    course_id: int, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить модальное окно курса"""
    logger.info(f"Admin {current_admin.username} fetching modal for course {course_id}")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(
            f"/v1/admin/course-modals/{course_id}", 
            headers=_hdr()
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

@router.post("/modal/{course_id}/")
async def create_course_modal(
    course_id: int, 
    title: str = Body(...), 
    blocks: List[Dict[str, Any]] = Body(...),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создать модальное окно для курса"""
    logger.info(f"Admin {current_admin.username} creating modal for course {course_id}")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.post(
            f"/v1/admin/course-modals/{course_id}", 
            headers=_hdr(),
            json={"title": title, "blocks": blocks}
        )
        if response.status_code == 400:
            raise HTTPException(status_code=400, detail="Модальное окно уже существует")
        response.raise_for_status()
        return response.json()

@router.put("/modal/{course_id}/")
async def update_course_modal(
    course_id: int, 
    title: Optional[str] = Body(None),
    blocks: Optional[List[Dict[str, Any]]] = Body(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновить модальное окно курса"""
    logger.info(f"Admin {current_admin.username} updating modal for course {course_id}")
    
    data: Dict[str, Any] = {}
    if title is not None:
        data["title"] = title
    if blocks is not None:
        data["blocks"] = blocks
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.put(
            f"/v1/admin/course-modals/{course_id}", 
            headers=_hdr(), 
            json=data
        )
        response.raise_for_status()
        return response.json()

@router.delete("/modal/{course_id}/")
async def delete_course_modal(
    course_id: int, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удалить модальное окно курса"""
    logger.info(f"Admin {current_admin.username} deleting modal for course {course_id}")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.delete(
            f"/v1/admin/course-modals/{course_id}", 
            headers=_hdr()
        )
        response.raise_for_status()
        return {"message": "Модальное окно удалено"}

# === РАБОТЫ УЧЕНИКОВ ===
@router.get("/student-works/{course_id}/")
async def get_student_works(
    course_id: int, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить секцию работ учеников"""
    logger.info(f"Admin {current_admin.username} fetching student works for course {course_id}")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(
            f"/v1/admin/student-works/{course_id}", 
            headers=_hdr()
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

@router.post("/student-works/{course_id}/")
async def create_student_works(
    course_id: int, 
    title: str = Body(...), 
    description: str = Body(...),
    works: List[Dict[str, Any]] = Body(default=[]),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создать секцию работ учеников"""
    logger.info(f"Admin {current_admin.username} creating student works for course {course_id}")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.post(
            f"/v1/admin/student-works/{course_id}",
            headers=_hdr(),
            json={"title": title, "description": description, "works": works}
        )
        if response.status_code == 400:
            raise HTTPException(status_code=400, detail="Секция работ уже существует")
        response.raise_for_status()
        return response.json()

@router.put("/student-works/{course_id}/")
async def update_student_works(
    course_id: int,
    title: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    works: Optional[List[Dict[str, Any]]] = Body(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновить секцию работ учеников"""
    logger.info(f"Admin {current_admin.username} updating student works for course {course_id}")
    
    data: Dict[str, Any] = {}
    if title is not None:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if works is not None:
        data["works"] = works
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.put(
            f"/v1/admin/student-works/{course_id}",
            headers=_hdr(),
            json=data
        )
        response.raise_for_status()
        return response.json()

@router.delete("/student-works/{course_id}/")
async def delete_student_works(
    course_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удалить секцию работ учеников"""
    logger.info(f"Admin {current_admin.username} deleting student works for course {course_id}")
    
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as client:
        response = await client.delete(
            f"/v1/admin/student-works/{course_id}",
            headers=_hdr()
        )
        response.raise_for_status()
        return {"message": "Секция работ учеников удалена"}