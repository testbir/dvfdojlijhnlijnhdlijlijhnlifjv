# admin_service/api/statistics.py

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import httpx
from utils.auth import get_current_admin_user
from models.admin import AdminUser
from core.config import settings
from collections import defaultdict
import logging
import os

router = APIRouter(prefix="/admin/statistics", tags=["Admin Statistics"])
logger = logging.getLogger(__name__)

from core.config import settings

AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL
def _hdr(): return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

# Настройки для HTTP клиента
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
        raise HTTPException(status_code=504, detail=f"Сервис недоступен: timeout")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при запросе к {url}: {e.response.status_code}")
        # Возвращаем None для некритичных ошибок, чтобы не ломать всю статистику
        return None
    except httpx.RequestError as e:
        logger.error(f"Ошибка соединения с {url}: {str(e)}")
        return None


@router.get("/", summary="Общая статистика платформы")
async def get_platform_statistics(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает общую статистику по платформе"""
    logger.info(f"Админ {current_admin.username} запрашивает общую статистику платформы")
    
    stats = {
        "users": {},
        "courses": {},
        "revenue": {},
        "popular_courses": [],
        "recent_activity": []
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Получаем статистику пользователей
            users_response = await make_http_request(
                client, "GET", 
                f"{AUTH_SERVICE_URL}/api/admin/statistics/users/"
            )
            if users_response:
                stats["users"] = users_response.json()
            else:
                stats["users"] = {
                    "total": 0,
                    "active_today": 0,
                    "new_this_week": 0,
                    "new_this_month": 0
                }
            
            # Получаем статистику курсов
            courses_response = await make_http_request(
                client, "GET",
                f"{CATALOG_SERVICE_URL}/internal/statistics/courses/"
            )
            if courses_response:
                stats["courses"] = courses_response.json()
            else:
                stats["courses"] = {
                    "total": 0,
                    "published": 0,
                    "free": 0,
                    "paid": 0
                }
            
            # Получаем статистику доходов
            revenue_response = await make_http_request(
                client, "GET",
                f"{CATALOG_SERVICE_URL}/internal/statistics/revenue/"
            )
            if revenue_response:
                stats["revenue"] = revenue_response.json()
            else:
                stats["revenue"] = {
                    "total": 0,
                    "this_month": 0,
                    "this_week": 0,
                    "today": 0
                }
            
            # Получаем популярные курсы
            popular_response = await make_http_request(
                client, "GET",
                f"{CATALOG_SERVICE_URL}/internal/statistics/popular-courses/",
                params={"limit": 10}
            )
            if popular_response:
                stats["popular_courses"] = popular_response.json()
            
            # Получаем недавнюю активность
            activity_response = await make_http_request(
                client, "GET",
                f"{CATALOG_SERVICE_URL}/internal/statistics/recent-activity/",
                params={"limit": 20}
            )
            if activity_response:
                stats["recent_activity"] = activity_response.json()
            
            # Добавляем метаинформацию
            stats["generated_at"] = datetime.utcnow().isoformat()
            stats["generated_by"] = current_admin.username
            
            return stats
            
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении статистики: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


@router.get("/users/", summary="Детальная статистика пользователей")
async def get_users_statistics(
    days: int = Query(30, ge=1, le=365),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает детальную статистику по пользователям"""
    logger.info(f"Админ {current_admin.username} запрашивает статистику пользователей за {days} дней")
    
    try:
        async with httpx.AsyncClient() as client:
            # Получаем детальную статистику пользователей
            response = await make_http_request(
                client, "GET",
                f"{AUTH_SERVICE_URL}/api/admin/statistics/users/detailed/",
                params={"days": days}
            )
            
            if response:
                return response.json()
            else:
                return {
                    "total_users": 0,
                    "new_registrations": [],
                    "active_users": [],
                    "user_growth": [],
                    "registration_sources": {},
                    "user_activity": {}
                }
                
    except Exception as e:
        logger.error(f"Ошибка при получении статистики пользователей: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики пользователей: {str(e)}")


@router.get("/courses/", summary="Статистика по курсам")
async def get_courses_statistics(
    days: int = Query(30, ge=1, le=365),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает статистику по курсам"""
    logger.info(f"Админ {current_admin.username} запрашивает статистику курсов за {days} дней")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "GET",
                f"{CATALOG_SERVICE_URL}/internal/statistics/courses/detailed/",
                params={"days": days}
            )
            
            if response:
                return response.json()
            else:
                return {
                    "total_courses": 0,
                    "course_completion_rates": [],
                    "most_popular": [],
                    "revenue_by_course": [],
                    "course_progress": {}
                }
                
    except Exception as e:
        logger.error(f"Ошибка при получении статистики курсов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики курсов: {str(e)}")


@router.get("/revenue/", summary="Статистика доходов")
async def get_revenue_statistics(
    start_date: Optional[date] = Query(None, description="Начальная дата"),
    end_date: Optional[date] = Query(None, description="Конечная дата"),
    group_by: str = Query("day", regex="^(day|week|month)$", description="Группировка данных"),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает статистику доходов"""
    logger.info(f"Админ {current_admin.username} запрашивает статистику доходов")
    
    # Устанавливаем даты по умолчанию
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    try:
        async with httpx.AsyncClient() as client:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "group_by": group_by
            }
            
            response = await make_http_request(
                client, "GET",
                f"{CATALOG_SERVICE_URL}/internal/statistics/revenue/detailed/",
                params=params
            )
            
            if response:
                return response.json()
            else:
                return {
                    "total_revenue": 0,
                    "revenue_timeline": [],
                    "revenue_by_course": [],
                    "payment_methods": {},
                    "refunds": 0
                }
                
    except Exception as e:
        logger.error(f"Ошибка при получении статистики доходов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики доходов: {str(e)}")


@router.get("/learning/", summary="Статистика обучения")
async def get_learning_statistics(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает статистику по обучению и прогрессу"""
    logger.info(f"Админ {current_admin.username} запрашивает статистику обучения")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await make_http_request(
                client, "GET",
                f"{CATALOG_SERVICE_URL}/internal/statistics/learning/"
            )
            
            if response:
                return response.json()
            else:
                return {
                    "total_enrollments": 0,
                    "completion_rate": 0,
                    "average_progress": 0,
                    "time_spent": {},
                    "module_completion": {},
                    "dropout_points": []
                }
                
    except Exception as e:
        logger.error(f"Ошибка при получении статистики обучения: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики обучения: {str(e)}")


@router.get("/performance/", summary="Статистика производительности системы")
async def get_performance_statistics(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает статистику производительности системы"""
    logger.info(f"Админ {current_admin.username} запрашивает статистику производительности")
    
    try:
        # Собираем статистику с разных сервисов
        stats = {
            "auth_service": {},
            "catalog_service": {},
            "admin_service": {
                "status": "online",
                "uptime": "unknown",
                "requests_count": "unknown"
            }
        }
        
        async with httpx.AsyncClient() as client:
            # Проверяем статус auth_service
            try:
                auth_response = await make_http_request(
                    client, "GET",
                    f"{AUTH_SERVICE_URL}/health/",
                )
                if auth_response:
                    stats["auth_service"] = auth_response.json()
                else:
                    stats["auth_service"] = {"status": "offline", "error": "No response"}
            except:
                stats["auth_service"] = {"status": "offline", "error": "Connection failed"}
            
            # Проверяем статус catalog_service
            try:
                catalog_response = await make_http_request(
                    client, "GET",
                    f"{CATALOG_SERVICE_URL}/health/",
                )
                if catalog_response:
                    stats["catalog_service"] = catalog_response.json()
                else:
                    stats["catalog_service"] = {"status": "offline", "error": "No response"}
            except:
                stats["catalog_service"] = {"status": "offline", "error": "Connection failed"}
        
        stats["generated_at"] = datetime.utcnow().isoformat()
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики производительности: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики производительности: {str(e)}")


@router.get("/export/", summary="Экспорт статистики")
async def export_statistics(
    format: str = Query("json", regex="^(json|csv|xlsx)$", description="Формат экспорта"),
    type: str = Query("all", regex="^(all|users|courses|revenue)$", description="Тип статистики"),
    days: int = Query(30, ge=1, le=365),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Экспортирует статистику в различных форматах"""
    logger.info(f"Админ {current_admin.username} экспортирует статистику (format={format}, type={type})")
    
    # TODO: Реализовать экспорт в CSV/XLSX
    if format in ["csv", "xlsx"]:
        raise HTTPException(status_code=501, detail=f"Экспорт в формате {format} пока не реализован")
    
    try:
        # Получаем нужную статистику
        if type == "users":
            return await get_users_statistics(days, current_admin)
        elif type == "courses":
            return await get_courses_statistics(days, current_admin)
        elif type == "revenue":
            return await get_revenue_statistics(None, None, "day", current_admin)
        else:  # all
            return await get_platform_statistics(current_admin)
            
    except Exception as e:
        logger.error(f"Ошибка при экспорте статистики: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта: {str(e)}")


@router.get("/real-time/", summary="Статистика в реальном времени")
async def get_realtime_statistics(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает статистику в реальном времени"""
    logger.info(f"Админ {current_admin.username} запрашивает статистику в реальном времени")
    
    try:
        stats = {
            "online_users": 0,
            "active_sessions": 0,
            "current_load": {},
            "recent_registrations": [],
            "recent_purchases": [],
            "system_status": {}
        }
        
        async with httpx.AsyncClient() as client:
            # Получаем данные о текущих пользователях онлайн
            try:
                online_response = await make_http_request(
                    client, "GET",
                    f"{AUTH_SERVICE_URL}/api/admin/real-time/online-users/"
                )
                if online_response:
                    stats["online_users"] = online_response.json().get("count", 0)
            except:
                pass
            
            # Получаем недавние активности
            try:
                activity_response = await make_http_request(
                    client, "GET",
                    f"{CATALOG_SERVICE_URL}/internal/real-time/recent-activity/"
                )
                if activity_response:
                    activity_data = activity_response.json()
                    stats["recent_purchases"] = activity_data.get("purchases", [])
                    stats["active_sessions"] = activity_data.get("active_sessions", 0)
            except:
                pass
        
        stats["timestamp"] = datetime.utcnow().isoformat()
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики в реальном времени: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")