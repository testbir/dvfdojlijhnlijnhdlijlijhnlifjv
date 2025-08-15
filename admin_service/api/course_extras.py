# admin_service/api/course_extras.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional, Dict, Any
import httpx
from admin_service.core.config import settings
from admin_service.utils.auth import get_current_admin_user
from admin_service.models.admin import AdminUser

router = APIRouter(prefix="/admin/course-extras", tags=["Course Extras"])

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL
def _hdr(): return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

# === МОДАЛЬНЫЕ ОКНА ===
@router.get("/modal/{course_id}/")
async def get_course_modal(course_id: int, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.get(f"/v1/admin/course-modals/by-course/{course_id}", headers=_hdr())
        if r.status_code == 404: return None
        r.raise_for_status(); return r.json()

@router.post("/modal/{course_id}/")
async def create_course_modal(course_id: int, title: str = Body(...), blocks: List[Dict[str, Any]] = Body(...),
                              current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.post(f"/v1/admin/course-modals/by-course/{course_id}", headers=_hdr(),
                         json={"title": title, "blocks": blocks})
        if r.status_code == 400:
            raise HTTPException(status_code=400, detail="Модалка уже существует")
        r.raise_for_status(); return r.json()

@router.put("/modal/{course_id}/")
async def update_course_modal(course_id: int, title: Optional[str] = Body(None),
                              blocks: Optional[List[Dict[str, Any]]] = Body(None),
                              current_admin: AdminUser = Depends(get_current_admin_user)):
    data: Dict[str, Any] = {}
    if title is not None: data["title"] = title
    if blocks is not None: data["blocks"] = blocks
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.put(f"/v1/admin/course-modals/by-course/{course_id}", headers=_hdr(), json=data)
        r.raise_for_status(); return r.json()

@router.delete("/modal/{course_id}/")
async def delete_course_modal(course_id: int, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.delete(f"/v1/admin/course-modals/by-course/{course_id}", headers=_hdr())
        r.raise_for_status(); return {"message": "deleted"}

# === РАБОТЫ УЧЕНИКОВ ===
@router.get("/student-works/{course_id}/")
async def get_student_works(course_id: int, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.get(f"/v1/admin/student-works/by-course/{course_id}", headers=_hdr())
        if r.status_code == 404: return None
        r.raise_for_status(); return r.json()

@router.post("/student-works/{course_id}/")
async def create_student_works(course_id: int, title: str = Body(...), description: str = Body(...),
                               works: List[Dict[str, Any]] = Body(default=[]),
                               current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.post(f"/v1/admin/student-works/by-course/{course_id}", headers=_hdr(),
                         json={"title": title, "description": description, "works": works})
        if r.status_code == 400:
            raise HTTPException(status_code=400, detail="Секция уже существует")
        r.raise_for_status(); return r.json()

@router.put("/student-works/{course_id}/")
async def update_student_works(course_id: int, title: Optional[str] = Body(None),
                               description: Optional[str] = Body(None),
                               works: Optional[List[Dict[str, Any]]] = Body(None),
                               current_admin: AdminUser = Depends(get_current_admin_user)):
    data: Dict[str, Any] = {}
    if title is not None: data["title"] = title
    if description is not None: data["description"] = description
    if works is not None: data["works"] = works
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.put(f"/v1/admin/student-works/by-course/{course_id}", headers=_hdr(), json=data)
        r.raise_for_status(); return r.json()

@router.delete("/student-works/{course_id}/")
async def delete_student_works(course_id: int, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=15.0) as c:
        r = await c.delete(f"/v1/admin/student-works/by-course/{course_id}", headers=_hdr())
        r.raise_for_status(); return {"message": "deleted"}
