# catalog_service/api/learning/course_learning.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime

from db.dependencies import get_db_session
from models.course import Course
from models.module import Module
from models.content import ContentBlock
from models.access import CourseAccess
from models.progress import UserModuleProgress
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
async def get_course_learning_data(
    course_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Получить данные курса для страницы обучения"""
    user_id = get_current_user_id(request)
    
    access_result = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    access_row = access_result.scalar_one_or_none()

    if access_row is None:
        # доступа нет – проверяем бесплатность курса
        course_result = await db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = course_result.scalar_one_or_none()
        if not course or not course.is_free:
            raise HTTPException(status_code=403, detail="Доступ запрещен")
    else:
        # доступ есть – курс берём прямо из связанного объекта
        course = access_row.course

        # Получаем группы из модулей (используем group_title)
        modules_result = await db.execute(
            select(Module)
            .where(Module.course_id == course_id)
            .order_by(Module.order)
        )
        modules = modules_result.scalars().all()
        
    # Извлекаем уникальные группы из group_title
    groups_dict = {}
    for module in modules:
        if module.group_title and module.group_title not in groups_dict:
            groups_dict[module.group_title] = {
                'id': module.group_title,  # Используем название как ID
                'title': module.group_title,
                'order': len(groups_dict)
            }
    
    groups = list(groups_dict.values())
    
    # Получаем прогресс из кэша или БД
    cached_progress = get_cached_user_progress(user_id, course_id)
    if cached_progress is not None:
        progress = cached_progress
    else:
        # Вычисляем прогресс
        total_modules = len(modules)
        if total_modules > 0:
            completed_result = await db.execute(
                select(func.count(UserModuleProgress.id))
                .where(
                    and_(
                        UserModuleProgress.user_id == user_id,
                        UserModuleProgress.module_id.in_([m.id for m in modules])
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
        groups=groups,
        modules=[
            ModuleResponse(
                id=str(m.id),
                title=m.title,
                groupId=m.group_title if m.group_title else "",
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
    
    # Для сохранения позиции используем UserModuleProgress
    # с дополнительным полем, если нужно (или просто отмечаем как частично пройденный)
    module_id = int(position_data.moduleId)
    
    # Проверяем существование записи
    progress_result = await db.execute(
        select(UserModuleProgress).where(
            and_(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id == module_id
            )
        )
    )
    progress = progress_result.scalar_one_or_none()
    
    if not progress:
        # Создаем запись, но не отмечаем как завершенную
        progress = UserModuleProgress(
            user_id=user_id,
            module_id=module_id,
            completed_at=None  # Не завершен, просто сохраняем позицию
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