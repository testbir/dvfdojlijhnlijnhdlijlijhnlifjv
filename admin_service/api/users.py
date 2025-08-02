# admin_service/api/users.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from db import get_db
from utils.auth import get_current_user
import httpx
from core.config import settings

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])

# Используем auth_service для получения данных о пользователях
AUTH_SERVICE_URL = "http://auth_service:8000"
CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL


@router.get("/", summary="Получить список всех пользователей")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    user_id: str = Depends(get_current_user)
):
    """Получает список пользователей из auth_service с дополнительной информацией"""
    try:
        # Получаем пользователей из auth_service
        async with httpx.AsyncClient() as client:
            params = {"page": page, "limit": limit}
            if search:
                params["search"] = search
                
            auth_response = await client.get(
                f"{AUTH_SERVICE_URL}/api/admin/users/",
                params=params
            )
            auth_response.raise_for_status()
            users_data = auth_response.json()
            
            # Для каждого пользователя получаем количество купленных курсов
            for user in users_data.get("users", []):
                courses_response = await client.get(
                    f"{CATALOG_SERVICE_URL}/internal/users/{user['id']}/courses-count/"
                )
                if courses_response.status_code == 200:
                    user["courses_purchased"] = courses_response.json().get("count", 0)
                else:
                    user["courses_purchased"] = 0
                    
        return users_data
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении пользователей: {str(e)}")


@router.get("/{user_id}/courses/", summary="Получить курсы пользователя")
async def get_user_courses(
    user_id: int,
    admin_id: str = Depends(get_current_user)
):
    """Получает список курсов, к которым у пользователя есть доступ"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/courses/"
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@router.patch("/{user_id}/toggle-active/", summary="Активировать/деактивировать пользователя")
async def toggle_user_active(
    user_id: int,
    is_active: bool,
    admin_id: str = Depends(get_current_user)
):
    """Изменяет статус активности пользователя"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/toggle-active/",
                json={"is_active": is_active}
            )
            response.raise_for_status()
            return {"success": True, "is_active": is_active}
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@router.post("/{user_id}/grant-access/", summary="Предоставить доступ к курсу")
async def grant_course_access(
    user_id: int,
    course_id: int,
    admin_id: str = Depends(get_current_user)
):
    """Предоставляет пользователю доступ к курсу"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/grant-access/",
                json={"course_id": course_id}
            )
            response.raise_for_status()
            return {"success": True, "message": "Доступ предоставлен"}
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            raise HTTPException(status_code=409, detail="У пользователя уже есть доступ к этому курсу")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@router.post("/{user_id}/remove-access/", summary="Отозвать доступ к курсу")
async def remove_course_access(
    user_id: int,
    course_id: int,
    admin_id: str = Depends(get_current_user)
):
    """Отзывает у пользователя доступ к курсу"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/remove-access/{course_id}/"
            )
            response.raise_for_status()
            return {"success": True, "message": "Доступ отозван"}
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@router.get("/{user_id}/activity/", summary="История активности пользователя")
async def get_user_activity(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    admin_id: str = Depends(get_current_user)
):
    """Получает историю активности пользователя"""
    try:
        async with httpx.AsyncClient() as client:
            # Получаем прогресс по курсам
            progress_response = await client.get(
                f"{CATALOG_SERVICE_URL}/internal/users/{user_id}/progress/"
            )
            
            # Получаем историю входов
            auth_response = await client.get(
                f"{AUTH_SERVICE_URL}/api/admin/users/{user_id}/login-history/",
                params={"days": days}
            )
            
            return {
                "progress": progress_response.json() if progress_response.status_code == 200 else [],
                "login_history": auth_response.json() if auth_response.status_code == 200 else []
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении активности: {str(e)}")