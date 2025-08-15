# admin_service/services/catalog_api.py

import httpx
from admin_service.core.config import settings

def _headers():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

async def list_courses(params: dict | None = None):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.get("/v1/admin/courses", headers=_headers(), params=params)
        r.raise_for_status(); return r.json()

async def get_course(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.get(f"/v1/admin/courses/{course_id}", headers=_headers())
        r.raise_for_status(); return r.json()

async def create_course(payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.post("/v1/admin/courses", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def update_course(course_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.patch(f"/v1/admin/courses/{course_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_course(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.delete(f"/v1/admin/courses/{course_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}
