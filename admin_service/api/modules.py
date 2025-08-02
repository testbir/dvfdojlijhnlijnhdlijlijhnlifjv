# admin_service/api/modules.py


import httpx
from fastapi import APIRouter, HTTPException
from schemas import ModuleCreate
from core.config import settings
from services.catalog_api import (get_module, 
                                  update_module, 
                                  delete_module, 
                                  get_modules_for_course)
from utils.auth import get_current_user
from fastapi import Depends

router = APIRouter()
CATALOG_URL = settings.CATALOG_SERVICE_URL


@router.post("/admin/courses/{course_id}/modules/", summary="Создать модуль для курса")
async def create_module(course_id: int, data: ModuleCreate, user_id: str = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{CATALOG_URL}/courses/internal/courses/{course_id}/modules/",
                json=data.dict()
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        return response.json()



@router.get("/admin/modules/{module_id}", summary="Получить модуль по ID")
async def retrieve_module(module_id: int, user_id: str = Depends(get_current_user)):
    return await get_module(module_id)

@router.put("/admin/modules/{module_id}", summary="Обновить модуль по ID")
async def edit_module(module_id: int, data: ModuleCreate, user_id: str = Depends(get_current_user)):
    return await update_module(module_id, data)

@router.delete("/admin/modules/{module_id}", summary="Удалить модуль по ID")
async def remove_module(module_id: int, user_id: str = Depends(get_current_user)):
    return await delete_module(module_id)


@router.get("/admin/courses/{course_id}/modules/", summary="Получить список модулей для курса")
async def list_modules_for_course(course_id: int, user_id: str = Depends(get_current_user)):
    return await get_modules_for_course(course_id)


