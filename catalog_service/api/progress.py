# catalog_service/api/progress.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.dependencies import get_db_session
from models.module import Module
from models.access import CourseAccess
from models.progress import UserModuleProgress
from utils.auth import get_current_user_id
from datetime import datetime
from schemas.module import ModuleContentSchema
from models.content import ContentBlock
from typing import List
from models.course import Course
from schemas.progress import CourseProgressSchema, SingleCourseProgressSchema
from utils.rate_limit import limiter

router = APIRouter()

@router.post("/courses/{course_id}/module/{module_id}/complete/", summary="Завершить модуль")
@limiter.limit("10/minute")
async def complete_module(course_id: int, module_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)

    # Проверяем существование модуля
    result = await db.execute(
        select(Module).where(
            Module.id == module_id,
            Module.course_id == course_id
        )
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")

    # Проверяем курс и доступ
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    if not course.is_free:
        result = await db.execute(
            select(CourseAccess).where(
                CourseAccess.user_id == user_id,
                CourseAccess.course_id == course_id
            )
        )
        access = result.scalar_one_or_none()
        if not access:
            raise HTTPException(status_code=403, detail="Нет доступа к курсу")

    # Проверяем, не завершен ли уже модуль
    result = await db.execute(
        select(UserModuleProgress).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id == module_id
        )
    )
    existing_progress = result.scalar_one_or_none()
    if existing_progress:
        return {"success": True, "message": "Модуль уже был завершён ранее"}

    # Создаем запись о прогрессе
    progress = UserModuleProgress(
        user_id=user_id,
        module_id=module_id,
        completed_at=datetime.utcnow()
    )
    db.add(progress)
    await db.commit()

    return {"success": True, "message": "Модуль успешно завершён"}

@router.get("/courses/{course_id}/module/{module_id}/", response_model=ModuleContentSchema, summary="Контент модуля")
async def get_module_content(course_id: int, module_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)  # Требует авторизации

    # Проверяем существование модуля
    result = await db.execute(
        select(Module).where(
            Module.id == module_id,
            Module.course_id == course_id
        )
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")

    # Проверяем доступ к курсу
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Если курс бесплатный - доступ есть у всех авторизованных
    # Если платный - проверяем покупку
    if not course.is_free:
        result = await db.execute(
            select(CourseAccess).where(
                CourseAccess.user_id == user_id,
                CourseAccess.course_id == course_id
            )
        )
        access = result.scalar_one_or_none()
        if not access:
            raise HTTPException(status_code=403, detail="Нет доступа к курсу")

    # Получаем блоки контента модуля
    result = await db.execute(
        select(ContentBlock)
        .where(ContentBlock.module_id == module_id)
        .order_by(ContentBlock.order)
    )
    blocks = result.scalars().all()

    # Проверяем, завершен ли модуль пользователем
    result = await db.execute(
        select(UserModuleProgress).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id == module_id
        )
    )
    is_completed = result.scalar_one_or_none() is not None

    return {
        "module_id": module.id,
        "title": module.title,
        "blocks": blocks,
        "is_completed": is_completed
    }

@router.get("/", response_model=List[CourseProgressSchema], summary="Прогресс по всем курсам")
async def all_course_progress(request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)

    # Получаем все курсы пользователя
    result = await db.execute(
        select(CourseAccess).where(CourseAccess.user_id == user_id)
    )
    accesses = result.scalars().all()
    
    result_list = []

    for access in accesses:
        # Получаем информацию о курсе
        course_result = await db.execute(
            select(Course).where(Course.id == access.course_id)
        )
        course = course_result.scalar_one_or_none()
        if not course:
            continue
            
        # Получаем все модули курса
        modules_result = await db.execute(
            select(Module).where(Module.course_id == course.id)
        )
        modules = modules_result.scalars().all()
        total_modules = len(modules)
        module_ids = [m.id for m in modules]

        # Считаем завершенные модули
        completed_result = await db.execute(
            select(func.count(UserModuleProgress.id)).where(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id.in_(module_ids)
            )
        )
        completed_count = completed_result.scalar()

        percent = round(completed_count / total_modules * 100, 1) if total_modules > 0 else 0

        result_list.append({
            "course_id": course.id,
            "course_title": course.title,
            "total_modules": total_modules,
            "completed_modules": completed_count,
            "progress_percent": percent
        })

    return result_list

@router.get("/{course_id}/", response_model=SingleCourseProgressSchema, summary="Прогресс по курсу")
async def single_course_progress(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)

    # Проверяем доступ к курсу
    result = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    access = result.scalar_one_or_none()
    if not access:
        raise HTTPException(status_code=403, detail="Нет доступа к курсу")

    # Получаем информацию о курсе
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Получаем все модули курса
    result = await db.execute(
        select(Module).where(Module.course_id == course_id)
    )
    modules = result.scalars().all()
    total_modules = len(modules)
    module_ids = [m.id for m in modules]

    # Получаем завершенные модули
    result = await db.execute(
        select(UserModuleProgress.module_id).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id.in_(module_ids)
        )
    )
    completed = result.scalars().all()
    completed_ids = list(completed)

    percent = round(len(completed_ids) / total_modules * 100, 1) if total_modules > 0 else 0

    return {
        "course_id": course.id,
        "course_title": course.title,
        "total_modules": total_modules,
        "completed_modules": completed_ids,
        "progress_percent": percent
    }