# admin_service/services/learning_service.py

import httpx
from admin_service.core.config import settings

def _headers():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

async def create_module(course_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.LEARNING_SERVICE_URL, timeout=10.0) as c:
        r = await c.post(f"/v1/admin/courses/{course_id}/modules", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def update_module(module_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.LEARNING_SERVICE_URL, timeout=10.0) as c:
        r = await c.patch(f"/v1/admin/modules/{module_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_module(module_id: int):
    async with httpx.AsyncClient(base_url=settings.LEARNING_SERVICE_URL, timeout=10.0) as c:
        r = await c.delete(f"/v1/admin/modules/{module_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

async def create_block(module_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.LEARNING_SERVICE_URL, timeout=10.0) as c:
        r = await c.post(f"/v1/admin/modules/{module_id}/blocks", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def update_block(block_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.LEARNING_SERVICE_URL, timeout=10.0) as c:
        r = await c.patch(f"/v1/admin/blocks/{block_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_block(block_id: int):
    async with httpx.AsyncClient(base_url=settings.LEARNING_SERVICE_URL, timeout=10.0) as c:
        r = await c.delete(f"/v1/admin/blocks/{block_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}
