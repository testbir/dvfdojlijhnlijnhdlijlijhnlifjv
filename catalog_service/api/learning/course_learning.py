# catalog_service/api/learning/course_learning.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from db.dependencies import get_db_session
from models.course import Course
from models.module import Module
from models.content import ContentBlock
from models.access import CourseAccess
from models.progress import UserModuleProgress
from utils.auth import get_current_user_id

router = APIRouter()

@router.get("/{course_id}/welcome/", summary="Страница приветствия после покупки")
async def course_welcome(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Страница приветствия после успешной покупки курса
    """
    user_id = get_current_user_id(request)
    
    # Проверяем курс
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Проверяем доступ
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
    
    # Считаем общее количество модулей
    total_modules_result = await db.execute(
        select(func.count(Module.id)).where(Module.course_id == course_id)
    )
    total_modules = total_modules_result.scalar() or 0
    
    return {
        "course_id": course.id,
        "course_title": course.title,
        "course_description": course.short_description,
        "total_modules": total_modules,
        "learning_url": f"/learning/courses/{course_id}/",
        "message": "🎉 Поздравляем! Курс теперь ваш. Начните обучение прямо сейчас!"
    }

@router.get("/{course_id}/", summary="Главная страница обучения")
async def course_learning_interface(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Основной интерфейс обучения курса
    Возвращает данные для шторки, сайдбара и контента
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
    
    # Получаем все модули курса
    modules_result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.order)
    )
    modules = modules_result.scalars().all()
    
    # Формируем данные для сайдбара
    sidebar_modules = []
    completed_modules_count = 0
    current_module = None
    
    for module in modules:
        # Проверяем завершенность модуля
        progress_result = await db.execute(
            select(UserModuleProgress).where(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id == module.id
            )
        )
        is_completed = progress_result.scalar_one_or_none() is not None
        
        if is_completed:
            completed_modules_count += 1
            status = "completed"
        else:
            status = "current" if current_module is None else "locked"
            if current_module is None:
                current_module = module
        
        sidebar_modules.append({
            "id": module.id,
            "title": module.title,
            "group_title": module.group_title,
            "order": module.order,
            "status": status
        })
    
    # Если нет текущего модуля (все завершены), берем первый
    if current_module is None and modules:
        current_module = modules[0]
    
    # Получаем блоки текущего модуля
    current_module_blocks = []
    if current_module:
        blocks_result = await db.execute(
            select(ContentBlock)
            .where(ContentBlock.module_id == current_module.id)
            .order_by(ContentBlock.order)
        )
        blocks = blocks_result.scalars().all()
        
        for block in blocks:
            current_module_blocks.append({
                "id": block.id,
                "type": block.type,
                "title": block.title,
                "content": block.content,
                "order": block.order,
                "video_preview": block.video_preview
            })
    
    # Вычисляем прогресс
    total_modules = len(modules)
    progress_percent = round((completed_modules_count / total_modules * 100) if total_modules > 0 else 0, 1)
    
    return {
        "header": {
            "course_title": course.title,
            "progress_percent": progress_percent
        },
        "sidebar": {
            "modules": sidebar_modules
        },
        "content": {
            "current_module": {
                "id": current_module.id if current_module else None,
                "title": current_module.title if current_module else None,
                "group_title": current_module.group_title if current_module else None
            },
            "blocks": current_module_blocks,
            "can_complete_module": len(current_module_blocks) > 0
        }
    }

@router.get("/{course_id}/modules/{module_id}/", summary="Загрузить конкретный модуль")
async def load_module_content(course_id: int, module_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Загружает контент конкретного модуля для отображения
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
    
    # Получаем блоки модуля
    blocks_result = await db.execute(
        select(ContentBlock)
        .where(ContentBlock.module_id == module_id)
        .order_by(ContentBlock.order)
    )
    blocks = blocks_result.scalars().all()
    
    # Проверяем завершенность модуля
    progress_result = await db.execute(
        select(UserModuleProgress).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id == module_id
        )
    )
    is_completed = progress_result.scalar_one_or_none() is not None
    
    return {
        "module": {
            "id": module.id,
            "title": module.title,
            "group_title": module.group_title,
            "is_completed": is_completed
        },
        "blocks": [
            {
                "id": block.id,
                "type": block.type,
                "title": block.title,
                "content": block.content,
                "order": block.order,
                "video_preview": block.video_preview
            }
            for block in blocks
        ]
    }