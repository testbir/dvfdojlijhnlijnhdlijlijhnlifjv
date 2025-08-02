# admin_service/api/bulk_operations.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
from utils.auth import get_current_user
import httpx
from core.config import settings

router = APIRouter(prefix="/admin/bulk-operations", tags=["Bulk Operations"])

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL
AUTH_SERVICE_URL = "http://auth_service:8000"


@router.post("/courses/", summary="Массовые операции с курсами")
async def bulk_course_operations(
    operation: str = Body(...),
    ids: List[int] = Body(...),
    params: Dict[str, Any] = Body(default={}),
    user_id: str = Depends(get_current_user)
):
    """
    Выполняет массовые операции над курсами
    
    Операции:
    - delete: удалить выбранные курсы
    - toggle_free: переключить бесплатный/платный статус
    - apply_discount: применить скидку
    - reorder: изменить порядок
    - duplicate: дублировать курсы
    """
    
    if not ids:
        raise HTTPException(status_code=400, detail="Не выбраны курсы")
    
    try:
        async with httpx.AsyncClient() as client:
            
            if operation == "delete":
                results = []
                for course_id in ids:
                    response = await client.delete(
                        f"{CATALOG_SERVICE_URL}/internal/courses/{course_id}"
                    )
                    results.append({
                        "id": course_id,
                        "success": response.status_code == 200
                    })
                return {"operation": "delete", "results": results}
            
            elif operation == "toggle_free":
                results = []
                for course_id in ids:
                    # Сначала получаем текущий статус
                    get_response = await client.get(
                        f"{CATALOG_SERVICE_URL}/courses/{course_id}/"
                    )
                    if get_response.status_code == 200:
                        course = get_response.json()
                        # Переключаем статус
                        update_response = await client.put(
                            f"{CATALOG_SERVICE_URL}/internal/courses/{course_id}",
                            json={"is_free": not course["is_free"]}
                        )
                        results.append({
                            "id": course_id,
                            "success": update_response.status_code == 200,
                            "is_free": not course["is_free"]
                        })
                return {"operation": "toggle_free", "results": results}
            
            elif operation == "apply_discount":
                discount = params.get("discount", 0)
                if not 0 <= discount <= 100:
                    raise HTTPException(status_code=400, detail="Скидка должна быть от 0 до 100")
                
                results = []
                for course_id in ids:
                    response = await client.patch(
                        f"{CATALOG_SERVICE_URL}/internal/courses/{course_id}/discount",
                        json={"discount": discount}
                    )
                    results.append({
                        "id": course_id,
                        "success": response.status_code == 200
                    })
                return {"operation": "apply_discount", "discount": discount, "results": results}
            
            elif operation == "reorder":
                start_order = params.get("start_order", 0)
                results = []
                for i, course_id in enumerate(ids):
                    response = await client.patch(
                        f"{CATALOG_SERVICE_URL}/internal/courses/{course_id}/order",
                        json={"order": start_order + i}
                    )
                    results.append({
                        "id": course_id,
                        "success": response.status_code == 200,
                        "order": start_order + i
                    })
                return {"operation": "reorder", "results": results}
            
            elif operation == "duplicate":
                results = []
                for course_id in ids:
                    response = await client.post(
                        f"{CATALOG_SERVICE_URL}/internal/courses/{course_id}/duplicate/"
                    )
                    results.append({
                        "id": course_id,
                        "success": response.status_code == 200,
                        "new_id": response.json().get("id") if response.status_code == 200 else None
                    })
                return {"operation": "duplicate", "results": results}
            
            else:
                raise HTTPException(status_code=400, detail=f"Неизвестная операция: {operation}")
                
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@router.post("/modules/", summary="Массовые операции с модулями")
async def bulk_module_operations(
    operation: str = Body(...),
    ids: List[int] = Body(...),
    params: Dict[str, Any] = Body(default={}),
    user_id: str = Depends(get_current_user)
):
    """
    Выполняет массовые операции над модулями
    """
    
    if not ids:
        raise HTTPException(status_code=400, detail="Не выбраны модули")
    
    try:
        async with httpx.AsyncClient() as client:
            
            if operation == "delete":
                results = []
                for module_id in ids:
                    response = await client.delete(
                        f"{CATALOG_SERVICE_URL}/internal/modules/{module_id}"
                    )
                    results.append({
                        "id": module_id,
                        "success": response.status_code == 200
                    })
                return {"operation": "delete", "results": results}
            
            elif operation == "move":
                new_course_id = params.get("course_id")
                if not new_course_id:
                    raise HTTPException(status_code=400, detail="Не указан целевой курс")
                
                # Здесь должна быть логика перемещения модулей
                return {"operation": "move", "message": "Функция в разработке"}
            
            else:
                raise HTTPException(status_code=400, detail=f"Неизвестная операция: {operation}")
                
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@router.post("/users/", summary="Массовые операции с пользователями")
async def bulk_user_operations(
    operation: str = Body(...),
    ids: List[int] = Body(...),
    params: Dict[str, Any] = Body(default={}),
    user_id: str = Depends(get_current_user)
):
    """
    Выполняет массовые операции над пользователями
    """
    
    if not ids:
        raise HTTPException(status_code=400, detail="Не выбраны пользователи")
    
    try:
        async with httpx.AsyncClient() as client:
            
            if operation == "activate":
                results = []
                for user_id in ids:
                    response = await client.patch(
                        f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/toggle-active/",
                        json={"is_active": True}
                    )
                    results.append({
                        "id": user_id,
                        "success": response.status_code == 200
                    })
                return {"operation": "activate", "results": results}
            
            elif operation == "deactivate":
                results = []
                for user_id in ids:
                    response = await client.patch(
                        f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/toggle-active/",
                        json={"is_active": False}
                    )
                    results.append({
                        "id": user_id,
                        "success": response.status_code == 200
                    })
                return {"operation": "deactivate", "results": results}
            
            elif operation == "grant_course":
                course_id = params.get("course_id")
                if not course_id:
                    raise HTTPException(status_code=400, detail="Не указан курс")
                
                results = []
                for user_id in ids:
                    response = await client.post(
                        f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/grant-access/",
                        json={"course_id": course_id}
                    )
                    results.append({
                        "id": user_id,
                        "success": response.status_code == 200
                    })
                return {"operation": "grant_course", "course_id": course_id, "results": results}
            
            else:
                raise HTTPException(status_code=400, detail=f"Неизвестная операция: {operation}")
                
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))