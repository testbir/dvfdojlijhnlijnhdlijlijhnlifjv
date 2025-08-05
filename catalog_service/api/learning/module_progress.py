# catalog_service/api/learning/module_progress.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List
from datetime import datetime

from db.dependencies import get_db_session
from models.progress import UserProgress
from models.access import CourseAccess
from models.course import Course
from utils.auth import get_current_user_id
from utils.cache import invalidate_user_progress_cache
from schemas.learning import ModuleProgressResponse, CourseAccessResponse

router = APIRouter()


@router.post("/{course_id}/modules/{module_id}/complete")
async def mark_module_completed(
    course_id: int,
    module_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Отметить модуль как завершенный"""
    user_id = get_current_user_id(request)
    
    # Проверяем доступ
    has_access = await _check_course_access(db, user_id, course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Обновляем или создаем запись прогресса
    progress_result = await db.execute(
        select(UserProgress).where(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.course_id == course_id,
                UserProgress.module_id == module_id
            )
        )
    )
    progress = progress_result.scalar_one_or_none()
    
    if progress:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
        progress.updated_at = datetime.utcnow()
    else:
        progress = UserProgress(
            user_id=user_id,
            course_id=course_id,
            module_id=module_id,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        db.add(progress)
    
    await db.commit()
    
    # Инвалидируем кэш прогресса
    invalidate_user_progress_cache(user_id, course_id)
    
    return {"success": True}


@router.get("/{course_id}/progress", response_model=List[ModuleProgressResponse])
async def get_user_progress(
    course_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Получить прогресс пользователя по всем модулям курса"""
    user_id = get_current_user_id(request)
    
    # Проверяем доступ
    has_access = await _check_course_access(db, user_id, course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Получаем прогресс по всем модулям
    progress_result = await db.execute(
        select(UserProgress).where(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.course_id == course_id
            )
        )
    )
    progress_records = progress_result.scalars().all()
    
    return [
        ModuleProgressResponse(
            moduleId=str(p.module_id),
            isCompleted=p.is_completed,
            completedAt=p.completed_at
        ) for p in progress_records
    ]


@router.get("/{course_id}/access", response_model=CourseAccessResponse)
async def check_course_access(
    course_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Проверить доступ к курсу"""
    try:
        user_id = get_current_user_id(request)
    except:
        # Пользователь не авторизован
        return CourseAccessResponse(hasAccess=False)
    
    has_access = await _check_course_access(db, user_id, course_id)
    
    return CourseAccessResponse(hasAccess=has_access)


async def _check_course_access(db: AsyncSession, user_id: int, course_id: int) -> bool:
    """Внутренняя функция проверки доступа к курсу"""
    # Проверяем платный доступ
    access_result = await db.execute(
        select(CourseAccess).where(
            and_(
                CourseAccess.user_id == user_id,
                CourseAccess.course_id == course_id
            )
        )
    )
    if access_result.scalar_one_or_none():
        return True
    
    # Проверяем бесплатный курс
    course_result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = course_result.scalar_one_or_none()
    
    return course and course.is_free