# admin_service/api/course_extras.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional, Dict, Any
from utils.auth import get_current_user
from core.config import settings
import httpx

router = APIRouter(prefix="/admin/course-extras", tags=["Course Extras"])

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL

# === МОДАЛЬНЫЕ ОКНА ===

@router.get("/modal/{course_id}/", summary="Получить модальное окно курса")
async def get_course_modal(
    course_id: int,
    user_id: str = Depends(get_current_user)
):
    """Получает модальное окно для курса"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CATALOG_SERVICE_URL}/internal/course-modals/course/{course_id}/"
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.post("/modal/{course_id}/", summary="Создать модальное окно курса")
async def create_course_modal(
    course_id: int,
    title: str = Body(...),
    blocks: List[Dict[str, Any]] = Body(...),
    user_id: str = Depends(get_current_user)
):
    """Создает модальное окно для курса"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CATALOG_SERVICE_URL}/internal/course-modals/course/{course_id}/",
                json={
                    "title": title,
                    "blocks": blocks
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise HTTPException(status_code=400, detail="Модальное окно для этого курса уже существует")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.put("/modal/{course_id}/", summary="Обновить модальное окно курса")
async def update_course_modal(
    course_id: int,
    title: Optional[str] = Body(None),
    blocks: Optional[List[Dict[str, Any]]] = Body(None),
    user_id: str = Depends(get_current_user)
):
    """Обновляет модальное окно курса"""
    try:
        data = {}
        if title is not None:
            data["title"] = title
        if blocks is not None:
            data["blocks"] = blocks
            
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CATALOG_SERVICE_URL}/internal/course-modals/course/{course_id}/",
                json=data
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.delete("/modal/{course_id}/", summary="Удалить модальное окно курса")
async def delete_course_modal(
    course_id: int,
    user_id: str = Depends(get_current_user)
):
    """Удаляет модальное окно курса"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CATALOG_SERVICE_URL}/internal/course-modals/course/{course_id}/"
            )
            response.raise_for_status()
            return {"message": "Модальное окно удалено"}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

# === РАБОТЫ УЧЕНИКОВ ===

@router.get("/student-works/{course_id}/", summary="Получить работы учеников курса")
async def get_student_works(
    course_id: int,
    user_id: str = Depends(get_current_user)
):
    """Получает секцию работ учеников для курса"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CATALOG_SERVICE_URL}/internal/student-works/course/{course_id}/"
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.post("/student-works/{course_id}/", summary="Создать секцию работ учеников")
async def create_student_works(
    course_id: int,
    title: str = Body(...),
    description: str = Body(...),
    works: List[Dict[str, Any]] = Body(default=[]),
    user_id: str = Depends(get_current_user)
):
    """Создает секцию работ учеников для курса"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CATALOG_SERVICE_URL}/internal/student-works/course/{course_id}/",
                json={
                    "title": title,
                    "description": description,
                    "works": works
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise HTTPException(status_code=400, detail="Секция работ для этого курса уже существует")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.put("/student-works/{course_id}/", summary="Обновить секцию работ учеников")
async def update_student_works(
    course_id: int,
    title: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    works: Optional[List[Dict[str, Any]]] = Body(None),
    user_id: str = Depends(get_current_user)
):
    """Обновляет секцию работ учеников"""
    try:
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if works is not None:
            data["works"] = works
            
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CATALOG_SERVICE_URL}/internal/student-works/course/{course_id}/",
                json=data
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.delete("/student-works/{course_id}/", summary="Удалить секцию работ учеников")
async def delete_student_works(
    course_id: int,
    user_id: str = Depends(get_current_user)
):
    """Удаляет секцию работ учеников"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CATALOG_SERVICE_URL}/internal/student-works/course/{course_id}/"
            )
            response.raise_for_status()
            return {"message": "Секция работ учеников удалена"}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))