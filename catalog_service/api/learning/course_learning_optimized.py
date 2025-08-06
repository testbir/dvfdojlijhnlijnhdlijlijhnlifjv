# catalog_service/api/learning/course_learning_optimized.py

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
@cache_result(ttl=300, key_prefix="course_learning")
async def get_course_learning_data(
    course_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """Получить данные курса для страницы обучения"""
    user_id = get_current_user_id(request)

    # --- проверка доступа ----------------------------------------------------
    access_res = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id,
        )
    )
    access_row = access_res.scalar_one_or_none()

    if access_row is None:
        course_row = await db.execute(select(Course).where(Course.id == course_id))
        course = course_row.scalar_one_or_none()
        if not course or not course.is_free:
            raise HTTPException(status_code=403, detail="Доступ запрещен")
    else:
        # связи в модели нет, поэтому берём курс обычным запросом
        course_res = await db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = course_res.scalar_one()


    # --- берём все модули курса ----------------------------------------------
    modules_row = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.order)
    )
    modules = modules_row.scalars().all()

    # --- формируем группы из group_title -------------------------------------
    groups_dict: dict[str, dict] = {}
    for m in modules:
        if m.group_title and m.group_title not in groups_dict:
            groups_dict[m.group_title] = {
                "id": m.group_title,
                "title": m.group_title,
                "order": len(groups_dict),  # счётчик порядка групп
            }
    groups_resp = [GroupResponse(**g) for g in groups_dict.values()]

    # --- формируем список модулей для ответа ---------------------------------
    modules_resp = [
        ModuleResponse(
            id=str(m.id),
            title=m.title,
            groupId=m.group_title or "",
            order=m.order,
        )
        for m in modules
    ]

    # --- считаем прогресс -----------------------------------------------------
    cached = get_cached_user_progress(user_id, course_id)
    if cached is not None:
        progress = cached
    else:
        total = len(modules_resp)
        if total:
            done_row = await db.execute(
                select(func.count(UserModuleProgress.id)).where(
                    UserModuleProgress.user_id == user_id,
                    UserModuleProgress.module_id.in_([m.id for m in modules]),
                    UserModuleProgress.completed_at.is_not(None) 
                )
            )
            completed = done_row.scalar()
            progress = round(completed / total * 100, 1)
        else:
            progress = 0
        cache_user_progress(user_id, course_id, progress)

    # --- ответ ---------------------------------------------------------------
    return CourseDataResponse(
        id=str(course_id),
        title=course.title,
        groups=groups_resp,
        modules=modules_resp,
        progress=progress,
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
        select(UserModuleProgress).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id == int(position_data.moduleId),
        )
    )
    progress = progress_result.scalar_one_or_none()

    if progress is None:
        progress = UserModuleProgress(
            user_id=user_id,
            module_id=int(position_data.moduleId),
            completed_at=None,   # поле действительно существует
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