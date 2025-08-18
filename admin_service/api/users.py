# admin_service/api/users.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from db import get_db
import httpx
from core.config import settings
from utils.auth import get_current_admin_user
from models.admin import AdminUser
import logging
import os

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])
logger = logging.getLogger(__name__)

# Используем переменные окружения для URL сервисов
from core.config import settings
AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL
def _hdr(): return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

# Настройки для HTTP клиента
HTTP_TIMEOUT = 30.0
MAX_RETRIES = 3


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
        raise HTTPException(status_code=504, detail=f"Сервис недоступен: timeout")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при запросе к {url}: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"Ошибка внешнего сервиса: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Ошибка соединения с {url}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Сервис недоступен: {str(e)}")


@router.get("/", summary="Получить список всех пользователей")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получает список пользователей из auth_service с дополнительной информацией"""
    logger.info(f"Админ {current_admin.username} запрашивает список пользователей (page={page}, limit={limit})")
    
    try:
        async with httpx.AsyncClient() as client:
            # Получаем пользователей из auth_service
            params = {"page": page, "limit": limit}
            if search:
                params["search"] = search
                
            auth_response = await make_http_request(
                client, "GET", 
                f"{AUTH_SERVICE_URL}/api/admin/users/",
                params=params
            )
            users_data = auth_response.json()
            
            # Для каждого пользователя получаем количество купленных курсов
            for user in users_data.get("users", []):
                user_id = user.get("id")
                if user_id:
                    try:
                        # Получаем статистику курсов пользователя
                        courses_response = await make_http_request(
                            client, "GET",
                            f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/courses-count/"
                        )
                        courses_stats = courses_response.json()
                        user["courses_count"] = courses_stats.get("count", 0)
                        user["completed_courses"] = courses_stats.get("completed", 0)
                    except HTTPException:
                        # Если не удалось получить статистику курсов, ставим 0
                        user["courses_count"] = 0
                        user["completed_courses"] = 0
            
            return users_data
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении пользователей: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")


@router.get("/{user_id}", summary="Получить детальную информацию о пользователе")
async def get_user_detail(
    user_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получает детальную информацию о пользователе"""
    logger.info(f"Админ {current_admin.username} запрашивает данные пользователя {user_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Получаем основные данные пользователя
            user_response = await make_http_request(
                client, "GET",
                f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/"
            )
            user_data = user_response.json()
            
            # Получаем курсы пользователя
            try:
                courses_response = await make_http_request(
                    client, "GET",
                    f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/courses/"
                )
                user_data["courses"] = courses_response.json()
            except HTTPException:
                user_data["courses"] = []
            
            # Получаем прогресс обучения
            try:
                progress_response = await make_http_request(
                    client, "GET",
                    f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/progress/"
                )
                user_data["progress"] = progress_response.json()
            except HTTPException:
                user_data["progress"] = {}
            
            return user_data
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении данных пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")


@router.post("/{user_id}/ban/", summary="Заблокировать пользователя")
async def ban_user(
    user_id: int,
    reason: str = Query(..., description="Причина блокировки"),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Блокирует пользователя"""
    logger.warning(f"Админ {current_admin.username} блокирует пользователя {user_id}. Причина: {reason}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "POST",
                f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/ban/",
                json={"reason": reason, "banned_by": current_admin.username}
            )
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при блокировке пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка блокировки: {str(e)}")


@router.post("/{user_id}/unban/", summary="Разблокировать пользователя")
async def unban_user(
    user_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Разблокирует пользователя"""
    logger.info(f"Админ {current_admin.username} разблокирует пользователя {user_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "POST",
                f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/unban/",
                json={"unbanned_by": current_admin.username}
            )
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при разблокировке пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка разблокировки: {str(e)}")


@router.post("/{user_id}/grant-access/{course_id}", summary="Предоставить доступ к курсу")
async def grant_course_access(
    user_id: int,
    course_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Предоставляет пользователю доступ к курсу"""
    logger.info(f"Админ {current_admin.username} предоставляет доступ к курсу {course_id} пользователю {user_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "POST",
                f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/grant-access/{course_id}/",
                json={"granted_by": current_admin.username}
            )
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при предоставлении доступа к курсу {course_id} пользователю {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка предоставления доступа: {str(e)}")


@router.delete("/{user_id}/remove-access/{course_id}", summary="Отозвать доступ к курсу")
async def revoke_course_access(
    user_id: int,
    course_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Отзывает доступ пользователя к курсу"""
    logger.warning(f"Админ {current_admin.username} отзывает доступ к курсу {course_id} у пользователя {user_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "DELETE",
                f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/remove-access/{course_id}/",
                json={"revoked_by": current_admin.username}
            )
            return {"success": True, "message": "Доступ отозван"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при отзыве доступа к курсу {course_id} у пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка отзыва доступа: {str(e)}")


@router.get("/{user_id}/activity/", summary="История активности пользователя")
async def get_user_activity(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получает историю активности пользователя"""
    logger.info(f"Админ {current_admin.username} запрашивает активность пользователя {user_id} за {days} дней")
    
    try:
        async with httpx.AsyncClient() as client:
            activity_data = {}
            
            # Получаем прогресс по курсам
            try:
                progress_response = await make_http_request(
                    client, "GET",
                    f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/progress/"
                )
                activity_data["progress"] = progress_response.json()
            except HTTPException:
                activity_data["progress"] = []
            
            # Получаем историю входов
            try:
                auth_response = await make_http_request(
                    client, "GET",
                    f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/login-history/",
                    params={"days": days}
                )
                activity_data["login_history"] = auth_response.json()
            except HTTPException:
                activity_data["login_history"] = []
            
            # Получаем статистику обучения
            try:
                stats_response = await make_http_request(
                    client, "GET",
                    f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/learning-stats/",
                    params={"days": days}
                )
                activity_data["learning_stats"] = stats_response.json()
            except HTTPException:
                activity_data["learning_stats"] = {}
            
            return activity_data
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении активности пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения активности: {str(e)}")


@router.post("/{user_id}/reset-password", summary="Сбросить пароль пользователя")
async def reset_user_password(
    user_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Сбрасывает пароль пользователя и отправляет новый по email"""
    logger.warning(f"Админ {current_admin.username} сбрасывает пароль пользователю {user_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "POST",
                f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/reset-password/",
                json={"reset_by": current_admin.username}
            )
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при сбросе пароля пользователю {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сброса пароля: {str(e)}")


@router.get("/{user_id}/purchases/", summary="История покупок пользователя")
async def get_user_purchases(
    user_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получает историю покупок пользователя"""
    logger.info(f"Админ {current_admin.username} запрашивает историю покупок пользователя {user_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            # В будущем здесь будет запрос к payment service
            # Пока возвращаем данные из catalog service
            response = await make_http_request(
                client, "GET",
                f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/purchase-history/"
            )
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении истории покупок пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории покупок: {str(e)}")