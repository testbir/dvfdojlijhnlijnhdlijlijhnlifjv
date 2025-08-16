# admin_service/services/catalog_api.py

import httpx
from core.config import settings

def _headers():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

# --- Курсы ---
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
    # В каталоге обновление — через PUT
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.put(f"/v1/admin/courses/{course_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_course(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.delete(f"/v1/admin/courses/{course_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

# --- Баннеры ---
async def get_banners():
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.get("/v1/admin/banners/", headers=_headers())
        r.raise_for_status(); return r.json()

async def create_banner(payload: dict):
    data = {k: payload.get(k) for k in ("image", "order", "link")}
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.post("/v1/admin/banners/", headers=_headers(), json=data)
        r.raise_for_status(); return r.json()

async def update_banner(banner_id: int, payload: dict):
    data = {k: v for k, v in payload.items() if k in ("image", "order", "link")}
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.put(f"/v1/admin/banners/{banner_id}", headers=_headers(), json=data)
        r.raise_for_status(); return r.json()

async def delete_banner(banner_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.delete(f"/v1/admin/banners/{banner_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

# --- Промо ---
async def get_promos():
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.get("/v1/admin/promos/", headers=_headers())
        r.raise_for_status(); return r.json()

async def create_promo(payload: dict):
    data = {k: payload.get(k) for k in ("image", "course_id", "order")}
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.post("/v1/admin/promos/", headers=_headers(), json=data)
        r.raise_for_status(); return r.json()

async def delete_promo(promo_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        r = await c.delete(f"/v1/admin/promos/{promo_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}
