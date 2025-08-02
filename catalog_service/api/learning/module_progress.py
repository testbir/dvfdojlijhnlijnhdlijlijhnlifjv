# catalog_service/api/learning/module_progress.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from db.dependencies import get_db_session
from models.course import Course
from models.module import Module
from models.access import CourseAccess
from models.progress import UserModuleProgress
from utils.auth import get_current_user_id
from utils.rate_limit import limiter

router = APIRouter()

@router.post("/{course_id}/modules/{module_id}/complete/", summary="Завершить модуль")
@limiter.limit("10/minute")
async def complete_module(course_id: int, module_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Завершает модуль и возвращает информацию о следующем модуле
    """
    user_id = get_current_user_id(request)
    
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
    
    # Проверяем модуль
    result = await db.execute(
        select(Module).where(
            Module.id == module_id,
            Module.course_id == course_id
        )
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    
    # Проверяем, не завершен ли уже модуль
    result = await db.execute(
        select(UserModuleProgress).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id == module_id
        )
    )
    existing_progress = result.scalar_one_or_none()
    
    if not existing_progress:
        # Создаем запись о завершении модуля
        progress = UserModuleProgress(
            user_id=user_id,
            module_id=module_id,
            completed_at=datetime.utcnow()
        )
        db.add(progress)
        await db.commit()
    
    # Находим следующий модуль
    next_module_result = await db.execute(
        select(Module)
        .where(
            Module.course_id == course_id,
            Module.order > module.order
        )
        .order_by(Module.order)
        .limit(1)
    )
    next_module = next_module_result.scalar_one_or_none()
    
    # Проверяем, завершен ли весь курс
    all_modules_result = await db.execute(
        select(Module).where(Module.course_id == course_id)
    )
    all_modules = all_modules_result.scalars().all()
    all_module_ids = [m.id for m in all_modules]
    
    completed_modules_result = await db.execute(
        select(UserModuleProgress.module_id).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id.in_(all_module_ids)
        )
    )
    completed_module_ids = completed_modules_result.scalars().all()
    
    course_completed = len(completed_module_ids) == len(all_modules)
    
    return {
        "success": True,
        "message": "Модуль успешно завершен!" if not existing_progress else "Модуль уже был завершен",
        "next_module": {
            "id": next_module.id,
            "title": next_module.title,
            "group_title": next_module.group_title
        } if next_module else None,
        "course_completed": course_completed,
        "progress_updated": True
    }

@router.get("/{course_id}/progress/", summary="Общий прогресс по курсу")
async def get_course_progress(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Возвращает детальный прогресс пользователя по курсу
    """
    user_id = get_current_user_id(request)
    
    # Проверяем доступ к курсу
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
    
    # Получаем все модули курса
    modules_result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.order)
    )
    modules = modules_result.scalars().all()
    
    # Получаем завершенные модули
    completed_modules_result = await db.execute(
        select(UserModuleProgress.module_id, UserModuleProgress.completed_at)
        .where(UserModuleProgress.user_id == user_id)
    )
    completed_data = {row[0]: row[1] for row in completed_modules_result.all()}
    
    # Формируем детальный прогресс
    modules_progress = []
    completed_count = 0
    
    for module in modules:
        is_completed = module.id in completed_data
        if is_completed:
            completed_count += 1
            
        modules_progress.append({
            "id": module.id,
            "title": module.title,
            "group_title": module.group_title,
            "order": module.order,
            "is_completed": is_completed,
            "completed_at": completed_data.get(module.id).isoformat() if module.id in completed_data else None
        })
    
    total_modules = len(modules)
    progress_percent = round((completed_count / total_modules * 100) if total_modules > 0 else 0, 1)
    
    return {
        "course_id": course_id,
        "course_title": course.title,
        "progress_percent": progress_percent,
        "completed_modules": completed_count,
        "total_modules": total_modules,
        "modules": modules_progress,
        "course_completed": completed_count == total_modules
    }