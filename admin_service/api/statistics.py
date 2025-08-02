# admin_service/api/statistics.py

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from utils.auth import get_current_user
import httpx
from core.config import settings
from collections import defaultdict

router = APIRouter(prefix="/admin/statistics", tags=["Admin Statistics"])

AUTH_SERVICE_URL = "http://auth_service:8000"
CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL


@router.get("/", summary="Общая статистика платформы")
async def get_platform_statistics(
    user_id: str = Depends(get_current_user)
):
    """Возвращает общую статистику по платформе"""
    try:
        async with httpx.AsyncClient() as client:
            # Получаем статистику пользователей
            users_stats = await client.get(f"{AUTH_SERVICE_URL}/api/admin/statistics/users/")
            users_data = users_stats.json() if users_stats.status_code == 200 else {}
            
            # Получаем статистику курсов
            courses_stats = await client.get(f"{CATALOG_SERVICE_URL}/internal/statistics/courses/")
            courses_data = courses_stats.json() if courses_stats.status_code == 200 else {}
            
            # Получаем статистику доходов
            revenue_stats = await client.get(f"{CATALOG_SERVICE_URL}/internal/statistics/revenue/")
            revenue_data = revenue_stats.json() if revenue_stats.status_code == 200 else {}
            
            # Получаем популярные курсы
            popular_courses = await client.get(f"{CATALOG_SERVICE_URL}/internal/statistics/popular-courses/")
            popular_data = popular_courses.json() if popular_courses.status_code == 200 else []
            
            # Получаем активность пользователей за последние 30 дней
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            activity_stats = await client.get(
                f"{AUTH_SERVICE_URL}/api/admin/statistics/user-activity/",
                params={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
            )
            activity_data = activity_stats.json() if activity_stats.status_code == 200 else []
            
            # Получаем доходы по месяцам
            revenue_by_month = await client.get(
                f"{CATALOG_SERVICE_URL}/internal/statistics/revenue-by-month/",
                params={"months": 12}
            )
            revenue_monthly = revenue_by_month.json() if revenue_by_month.status_code == 200 else []
            
            return {
                "total_users": users_data.get("total", 0),
                "active_users": users_data.get("active", 0),
                "total_courses": courses_data.get("total", 0),
                "free_courses": courses_data.get("free", 0),
                "paid_courses": courses_data.get("paid", 0),
                "total_revenue": revenue_data.get("total", 0),
                "registrations_last_30_days": users_data.get("new_last_30_days", 0),
                "popular_courses": popular_data,
                "user_activity": activity_data,
                "revenue_by_month": revenue_monthly
            }
            
    except Exception as e:
        return {
            "error": f"Ошибка при получении статистики: {str(e)}",
            "total_users": 0,
            "active_users": 0,
            "total_courses": 0,
            "free_courses": 0,
            "paid_courses": 0,
            "total_revenue": 0,
            "registrations_last_30_days": 0,
            "popular_courses": [],
            "user_activity": [],
            "revenue_by_month": []
        }


@router.get("/courses/{course_id}/", summary="Статистика по конкретному курсу")
async def get_course_statistics(
    course_id: int,
    user_id: str = Depends(get_current_user)
):
    """Возвращает детальную статистику по курсу"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CATALOG_SERVICE_URL}/internal/statistics/courses/{course_id}/"
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        return {"error": f"Ошибка: {e.response.status_code}"}


@router.get("/export/", summary="Экспорт статистики")
async def export_statistics(
    format: str = Query("csv", regex="^(csv|xlsx)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_id: str = Depends(get_current_user)
):
    """Экспортирует статистику в CSV или XLSX формате"""
    # Здесь должна быть логика экспорта
    # Это заглушка для примера
    return {
        "message": f"Экспорт в формате {format} будет реализован",
        "start_date": start_date,
        "end_date": end_date
    }


@router.get("/realtime/", summary="Статистика в реальном времени")
async def get_realtime_statistics(
    user_id: str = Depends(get_current_user)
):
    """Возвращает статистику в реальном времени"""
    try:
        async with httpx.AsyncClient() as client:
            # Активные пользователи сейчас
            active_now = await client.get(f"{AUTH_SERVICE_URL}/api/admin/statistics/active-now/")
            
            # Последние регистрации
            recent_registrations = await client.get(
                f"{AUTH_SERVICE_URL}/api/admin/statistics/recent-registrations/",
                params={"limit": 10}
            )
            
            # Последние покупки
            recent_purchases = await client.get(
                f"{CATALOG_SERVICE_URL}/internal/statistics/recent-purchases/",
                params={"limit": 10}
            )
            
            return {
                "active_users_now": active_now.json().get("count", 0) if active_now.status_code == 200 else 0,
                "recent_registrations": recent_registrations.json() if recent_registrations.status_code == 200 else [],
                "recent_purchases": recent_purchases.json() if recent_purchases.status_code == 200 else []
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "active_users_now": 0,
            "recent_registrations": [],
            "recent_purchases": []
        }