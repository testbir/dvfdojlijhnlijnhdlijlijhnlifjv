# admin_service/api/modules.py

import httpx
from fastapi import APIRouter, HTTPException, Depends
from schemas import ModuleCreate
from core.config import settings
from utils.auth import get_current_admin_user
from models.admin import AdminUser
from services.catalog_api import (
    get_module, 
    update_module, 
    delete_module, 
    get_modules_for_course
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

CATALOG_URL = settings.CATALOG_SERVICE_URL
HTTP_TIMEOUT = 30.0


async def make_http_request(client: httpx.AsyncClient, method: str, url: str, **kwargs):
    """
    Обертка для HTTP запросов с обработкой ошибок
    """
    try:
        response = await client.request(method, url, timeout=HTTP_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response
    except httpx.TimeoutException:
        logger.error(f"Timeout при запросе к {url}")
        raise HTTPException(status_code=504, detail="Сервис недоступен: timeout")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при запросе к {url}: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"Ошибка catalog service: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Ошибка соединения с {url}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Catalog service недоступен: {str(e)}")


@router.post("/admin/courses/{course_id}/modules/", summary="Создать модуль для курса")
async def create_module(
    course_id: int, 
    data: ModuleCreate, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создает новый модуль в курсе"""
    logger.info(f"Админ {current_admin.username} создает модуль в курсе {course_id}: {data.title}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "POST",
                f"{CATALOG_URL}/courses/internal/courses/{course_id}/modules/",
                json=data.dict()
            )
            
            result = response.json()
            logger.info(f"Модуль успешно создан в курсе {course_id}: {result}")
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании модуля в курсе {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания модуля: {str(e)}")


@router.get("/admin/modules/{module_id}", summary="Получить модуль по ID")
async def retrieve_module(
    module_id: int, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получает детальную информацию о модуле"""
    logger.info(f"Админ {current_admin.username} запрашивает модуль {module_id}")
    
    try:
        return await get_module(module_id)
    except Exception as e:
        logger.error(f"Ошибка получения модуля {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения модуля: {str(e)}")


@router.put("/admin/modules/{module_id}", summary="Обновить модуль по ID")
async def edit_module(
    module_id: int, 
    data: ModuleCreate, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновляет существующий модуль"""
    logger.info(f"Админ {current_admin.username} обновляет модуль {module_id}: {data.title}")
    
    try:
        result = await update_module(module_id, data)
        logger.info(f"Модуль {module_id} успешно обновлен")
        return result
    except Exception as e:
        logger.error(f"Ошибка обновления модуля {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления модуля: {str(e)}")


@router.delete("/admin/modules/{module_id}", summary="Удалить модуль по ID")
async def remove_module(
    module_id: int, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удаляет модуль и все связанные блоки"""
    logger.warning(f"Админ {current_admin.username} удаляет модуль {module_id}")
    
    try:
        result = await delete_module(module_id)
        logger.info(f"Модуль {module_id} успешно удален")
        return result
    except Exception as e:
        logger.error(f"Ошибка удаления модуля {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления модуля: {str(e)}")


@router.get("/admin/courses/{course_id}/modules/", summary="Получить список модулей для курса")
async def list_modules_for_course(
    course_id: int, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получает список всех модулей в курсе"""
    logger.info(f"Админ {current_admin.username} запрашивает модули курса {course_id}")
    
    try:
        return await get_modules_for_course(course_id)
    except Exception as e:
        logger.error(f"Ошибка получения модулей курса {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения модулей: {str(e)}")


@router.post("/admin/modules/{module_id}/reorder/", summary="Изменить порядок модуля")
async def reorder_module(
    module_id: int,
    new_order: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Изменяет порядок модуля в курсе"""
    logger.info(f"Админ {current_admin.username} изменяет порядок модуля {module_id} на {new_order}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "POST",
                f"{CATALOG_URL}/courses/internal/modules/{module_id}/reorder/",
                json={"new_order": new_order, "updated_by": current_admin.username}
            )
            
            result = response.json()
            logger.info(f"Порядок модуля {module_id} успешно изменен")
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка изменения порядка модуля {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка изменения порядка: {str(e)}")


@router.post("/admin/modules/{module_id}/duplicate/", summary="Дублировать модуль")
async def duplicate_module(
    module_id: int,
    new_title: str = None,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создает копию модуля"""
    logger.info(f"Админ {current_admin.username} дублирует модуль {module_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            payload = {"duplicated_by": current_admin.username}
            if new_title:
                payload["new_title"] = new_title
                
            response = await make_http_request(
                client, "POST",
                f"{CATALOG_URL}/courses/internal/modules/{module_id}/duplicate/",
                json=payload
            )
            
            result = response.json()
            logger.info(f"Модуль {module_id} успешно дублирован: {result}")
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка дублирования модуля {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка дублирования модуля: {str(e)}")


@router.get("/admin/modules/{module_id}/statistics/", summary="Статистика модуля")
async def get_module_statistics(
    module_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получает статистику по модулю (прохождение, время и т.д.)"""
    logger.info(f"Админ {current_admin.username} запрашивает статистику модуля {module_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "GET",
                f"{CATALOG_URL}/internal/modules/{module_id}/statistics/"
            )
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения статистики модуля {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")