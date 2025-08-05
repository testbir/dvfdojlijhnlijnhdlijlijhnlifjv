# catalog_service/api/learning/course_learning_optimized.py

# catalog_service/api/learning/course_learning.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime

from db.dependencies import get_db_session
from models.course import Course
from models.module import Module, ModuleGroup
from models.content import ContentBlock
from models.access import CourseAccess
from models.progress import UserProgress
from utils.auth import get_current_user_id
from utils.cache import cache_result, get_cached_user_progress, cache_user_progress
from schemas.learning import (
    CourseDataResponse,
    GroupResponse, 
    ModuleResponse,
    ContentBlockResponse,
    UpdatePositionRequest
)

router = APIRouter()


@router.get("/{course_id}", response_model=CourseDataResponse)
@cache_result(ttl=300, key_prefix="course_learning")
async def get_course_learning_data(
    course_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Получить данные курса для страницы обучения"""
    user_id = get_current_user_id(request)
    
    # Проверяем доступ
    access = await db.execute(
        select(CourseAccess).where(
            and_(
                CourseAccess.user_id == user_id,
                CourseAccess.course_id == course_id
            )
        )
    )
    if not access.scalar_one_or_none():
        # Проверяем, может это бесплатный курс
        course_result = await db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = course_result.scalar_one_or_none()
        if not course or not course.is_free:
            raise HTTPException(status_code=403, detail="Доступ запрещен")
    else:
        course = access.scalar_one().course
    
    # Получаем группы модулей
    groups_result = await db.execute(
        select(ModuleGroup)
        .where(ModuleGroup.course_id == course_id)
        .order_by(ModuleGroup.order)
    )
    groups = groups_result.scalars().all()
    
    # Получаем модули
    modules_result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.order)
    )
    modules = modules_result.scalars().all()
    
    # Получаем прогресс из кэша или БД
    cached_progress = get_cached_user_progress(user_id, course_id)
    if cached_progress is not None:
        progress = cached_progress
    else:
        # Вычисляем прогресс
        total_modules = len(modules)
        if total_modules > 0:
            completed_result = await db.execute(
                select(func.count(UserProgress.id))
                .where(
                    and_(
                        UserProgress.user_id == user_id,
                        UserProgress.course_id == course_id,
                        UserProgress.is_completed == True
                    )
                )
            )
            completed_count = completed_result.scalar()
            progress = round((completed_count / total_modules) * 100, 1)
        else:
            progress = 0
        
        # Кэшируем прогресс
        cache_user_progress(user_id, course_id, progress)
    
    return CourseDataResponse(
        id=str(course_id),
        title=course.title,
        groups=[
            GroupResponse(
                id=str(g.id),
                title=g.title,
                order=g.order
            ) for g in groups
        ],
        modules=[
            ModuleResponse(
                id=str(m.id),
                title=m.title,
                groupId=str(m.group_id) if m.group_id else "",
                order=m.order
            ) for m in modules
        ],
        progress=progress
    )


@router.get("/{course_id}/modules/{module_id}/content", response_model=List[ContentBlockResponse])
async def get_module_content(
    course_id: int,
    module_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Получить контент модуля"""
    user_id = get_current_user_id(request)
    
    # Проверяем доступ к курсу
    has_access = await _check_course_access(db, user_id, course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Получаем блоки контента
    blocks_result = await db.execute(
        select(ContentBlock)
        .where(ContentBlock.module_id == module_id)
        .order_by(ContentBlock.order)
    )
    blocks = blocks_result.scalars().all()
    
    return [
        ContentBlockResponse(
            id=str(b.id),
            type=b.type,
            title=b.title,
            content=b.content,
            order=b.order
        ) for b in blocks
    ]


@router.put("/{course_id}/position")
async def update_user_position(
    course_id: int,
    position_data: UpdatePositionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Обновить позицию пользователя в курсе"""
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
                UserProgress.module_id == int(position_data.moduleId)
            )
        )
    )
    progress = progress_result.scalar_one_or_none()
    
    if progress:
        progress.last_position = position_data.position
        progress.updated_at = datetime.utcnow()
    else:
        progress = UserProgress(
            user_id=user_id,
            course_id=course_id,
            module_id=int(position_data.moduleId),
            last_position=position_data.position,
            is_completed=False
        )
        db.add(progress)
    
    await db.commit()
    
    return {"success": True}


async def _check_course_access(db: AsyncSession, user_id: int, course_id: int) -> bool:
    """Проверка доступа к курсу"""
    # Сначала проверяем платный доступ
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
    
    # Затем проверяем, не бесплатный ли курс
    course_result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = course_result.scalar_one_or_none()
    
    return course and course.is_free