# admin_service/api/bulk_operations.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
import httpx
from admin_service.core.config import settings
from admin_service.utils.auth import get_current_admin_user
from admin_service.models.admin import AdminUser

router = APIRouter(prefix="/admin/bulk-operations", tags=["Bulk Operations"])

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL
def _hdr(): return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

@router.post("/courses/")
async def bulk_course_operations(
    operation: str = Body(...),
    ids: List[int] = Body(...),
    params: Dict[str, Any] = Body(default={}),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    if not ids:
        raise HTTPException(status_code=400, detail="Не выбраны курсы")

    async with httpx.AsyncClient(base_url=CATALOG_SERVICE_URL, timeout=20.0) as c:
        if operation == "delete":
            results = []
            for course_id in ids:
                r = await c.delete(f"/v1/admin/courses/{course_id}", headers=_hdr())
                results.append({"id": course_id, "success": r.status_code == 200 or r.status_code == 204})
            return {"operation": "delete", "results": results}

        elif operation == "toggle_free":
            results = []
            for course_id in ids:
                g = await c.get(f"/v1/admin/courses/{course_id}", headers=_hdr())
                if g.status_code != 200:
                    results.append({"id": course_id, "success": False})
                    continue
                cur = g.json()
                u = await c.patch(f"/v1/admin/courses/{course_id}", headers=_hdr(), json={"is_free": not cur.get("is_free", False)})
                results.append({"id": course_id, "success": u.status_code == 200, "is_free": not cur.get("is_free", False)})
            return {"operation": "toggle_free", "results": results}

        elif operation == "apply_discount":
            discount = params.get("discount", 0)
            if not 0 <= float(discount) <= 100:
                raise HTTPException(status_code=400, detail="Скидка должна быть от 0 до 100")
            results = []
            for course_id in ids:
                r = await c.patch(f"/v1/admin/courses/{course_id}", headers=_hdr(), json={"discount": discount})
                results.append({"id": course_id, "success": r.status_code == 200})
            return {"operation": "apply_discount", "discount": discount, "results": results}

        elif operation == "reorder":
            start_order = int(params.get("start_order", 0))
            results = []
            for i, course_id in enumerate(ids):
                r = await c.patch(f"/v1/admin/courses/{course_id}", headers=_hdr(), json={"order": start_order + i})
                results.append({"id": course_id, "success": r.status_code == 200, "order": start_order + i})
            return {"operation": "reorder", "results": results}

        elif operation == "duplicate":
            raise HTTPException(status_code=501, detail="Дубликат курса не реализован на backend")

        else:
            raise HTTPException(status_code=400, detail=f"Неизвестная операция: {operation}")

@router.post("/modules/")
async def bulk_module_operations(
    operation: str = Body(...),
    ids: List[int] = Body(...),
    params: Dict[str, Any] = Body(default={}),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    if not ids:
        raise HTTPException(status_code=400, detail="Не выбраны модули")

    # Пока только удаление через каталог не реализуется. Модули живут в learning_service.
    raise HTTPException(status_code=501, detail="Массовые операции с модулями не реализованы")
