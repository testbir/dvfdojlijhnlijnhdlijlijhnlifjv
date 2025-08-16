# admin_service/services/catalog_api.py

import httpx
from core.config import settings

def _headers():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

# --- Курсы ---
async def list_courses(params: dict | None = None):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # ДОБАВЛЕН СЛЕШ В КОНЦЕ
        r = await c.get("/v1/admin/courses/", headers=_headers(), params=params)
        r.raise_for_status(); return r.json()

async def get_course(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно
        r = await c.get(f"/v1/admin/courses/{course_id}", headers=_headers())
        r.raise_for_status(); return r.json()

async def create_course(payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # ДОБАВЛЕН СЛЕШ В КОНЦЕ
        r = await c.post("/v1/admin/courses/", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def update_course(course_id: int, payload: dict):
    # В каталоге обновление — через PUT
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно
        r = await c.put(f"/v1/admin/courses/{course_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_course(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно
        r = await c.delete(f"/v1/admin/courses/{course_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

# --- Баннеры ---
async def get_banners():
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # СЛЕШ УЖЕ ЕСТЬ - правильно
        r = await c.get("/v1/admin/banners/", headers=_headers())
        r.raise_for_status(); return r.json()

async def create_banner(payload: dict):
    data = {k: payload.get(k) for k in ("image", "order", "link")}
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # СЛЕШ УЖЕ ЕСТЬ - правильно
        r = await c.post("/v1/admin/banners/", headers=_headers(), json=data)
        r.raise_for_status(); return r.json()

async def update_banner(banner_id: int, payload: dict):
    data = {k: v for k, v in payload.items() if k in ("image", "order", "link")}
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.put(f"/v1/admin/banners/{banner_id}", headers=_headers(), json=data)
        r.raise_for_status(); return r.json()

async def delete_banner(banner_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.delete(f"/v1/admin/banners/{banner_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

# --- Модальные окна ---
async def get_modal(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.get(f"/v1/admin/modals/{course_id}", headers=_headers())
        if r.status_code == 404: return None
        r.raise_for_status(); return r.json()

async def create_modal(course_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.post(f"/v1/admin/modals/{course_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def update_modal(course_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.put(f"/v1/admin/modals/{course_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_modal(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.delete(f"/v1/admin/modals/{course_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

# --- Работы учеников ---
async def get_student_works(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.get(f"/v1/admin/student-works/{course_id}", headers=_headers())
        if r.status_code == 404: return None
        r.raise_for_status(); return r.json()

async def create_student_works(course_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.post(f"/v1/admin/student-works/{course_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def update_student_works(course_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.put(f"/v1/admin/student-works/{course_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_student_works(course_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.delete(f"/v1/admin/student-works/{course_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

# --- Промокоды ---
async def get_promocodes():
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # ДОБАВЛЕН СЛЕШ В КОНЦЕ
        r = await c.get("/v1/admin/promocodes/", headers=_headers())
        r.raise_for_status(); return r.json()

async def create_promocode(payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # ДОБАВЛЕН СЛЕШ В КОНЦЕ
        r = await c.post("/v1/admin/promocodes/", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def update_promocode(promo_id: int, payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.put(f"/v1/admin/promocodes/{promo_id}", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_promocode(promo_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.delete(f"/v1/admin/promocodes/{promo_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

# --- Лид-магниты ---
async def get_lead_magnets():
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # ДОБАВЛЕН СЛЕШ В КОНЦЕ
        r = await c.get("/v1/admin/lead-magnets/", headers=_headers())
        r.raise_for_status(); return r.json()

async def create_lead_magnet(payload: dict):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # ДОБАВЛЕН СЛЕШ В КОНЦЕ
        r = await c.post("/v1/admin/lead-magnets/", headers=_headers(), json=payload)
        r.raise_for_status(); return r.json()

async def delete_lead_magnet(magnet_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.delete(f"/v1/admin/lead-magnets/{magnet_id}", headers=_headers())
        r.raise_for_status(); return {"success": True}

async def get_lead_magnet_stats(magnet_id: int):
    async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=10.0) as c:
        # БЕЗ СЛЕША - правильно (ID в конце)
        r = await c.get(f"/v1/admin/lead-magnets/{magnet_id}/stats", headers=_headers())
        r.raise_for_status(); return r.json()