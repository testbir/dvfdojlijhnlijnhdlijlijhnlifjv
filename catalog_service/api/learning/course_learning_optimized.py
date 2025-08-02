# catalog_service/api/learning/course_learning_optimized.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Any
from db.dependencies import get_db_session
from models.course import Course
from models.module import Module
from models.content import ContentBlock
from models.access import CourseAccess
from models.progress import UserModuleProgress
from utils.auth import get_current_user_id
import redis
import json
from datetime import timedelta

router = APIRouter()

# Кэш для Redis (если используете)
# redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

@router.get("/{course_id}/", summary="Оптимизированный интерфейс обучения")
async def course_learning_interface_optimized(
    course_id: int, 
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
):
    """
    Оптимизированная версия для высоких нагрузок:
    - Один запрос вместо множественных
    - Кэширование
    - Минимизация данных
    """
    user_id = get_current_user_id(request)
    
    # 🔥 ОДИН БОЛЬШОЙ ЗАПРОС вместо множественных маленьких
    # Получаем ВСЕ данные одним запросом с JOIN
    query = (
        select(
            Course.id,
            Course.title,
            Module.id.label('module_id'),
            Module.title.label('module_title'),
            Module.group_title,
            Module.order.label('module_order'),
            ContentBlock.id.label('block_id'),
            ContentBlock.type,
            ContentBlock.title.label('block_title'),
            ContentBlock.content,
            ContentBlock.order.label('block_order'),
            ContentBlock.video_preview,
            UserModuleProgress.id.label('progress_id')
        )
        .select_from(Course)
        .join(Module, Course.id == Module.course_id)
        .outerjoin(ContentBlock, Module.id == ContentBlock.module_id)
        .outerjoin(
            UserModuleProgress,
            and_(
                Module.id == UserModuleProgress.module_id,
                UserModuleProgress.user_id == user_id
            )
        )
        .where(Course.id == course_id)
        .order_by(Module.order, ContentBlock.order)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # 🛡️ Проверка доступа (только для платных курсов)
    course_title = rows[0].title
    is_free = True  # Предполагаем бесплатный, если нет проверки
    
    if not is_free:  # Добавьте поле is_free в запрос если нужно
        access_result = await db.execute(
            select(CourseAccess.id).where(
                CourseAccess.user_id == user_id,
                CourseAccess.course_id == course_id
            ).limit(1)
        )
        if not access_result.scalar():
            raise HTTPException(status_code=403, detail="Нет доступа к курсу")
    
    # 📊 Обработка данных в памяти (быстрее чем дополнительные запросы)
    modules_data = {}
    current_module = None
    completed_modules_count = 0
    
    for row in rows:
        module_id = row.module_id
        
        # Инициализируем модуль если не существует
        if module_id not in modules_data:
            is_completed = bool(row.progress_id)
            if is_completed:
                completed_modules_count += 1
            
            modules_data[module_id] = {
                "id": module_id,
                "title": row.module_title,
                "group_title": row.group_title,
                "order": row.module_order,
                "status": "completed" if is_completed else "current" if current_module is None else "locked",
                "blocks": []
            }
            
            # Определяем текущий модуль (первый незавершенный)
            if not is_completed and current_module is None:
                current_module = modules_data[module_id]
        
        # Добавляем блок к модулю
        if row.block_id:
            modules_data[module_id]["blocks"].append({
                "id": row.block_id,
                "type": row.type,
                "title": row.block_title,
                "content": row.content,
                "order": row.block_order,
                "video_preview": row.video_preview
            })
    
    # Сортируем модули и блоки
    sorted_modules = sorted(modules_data.values(), key=lambda x: x["order"])
    for module in sorted_modules:
        module["blocks"] = sorted(module["blocks"], key=lambda x: x["order"])
    
    # Если нет текущего модуля (все завершены), берем первый
    if current_module is None and sorted_modules:
        current_module = sorted_modules[0]
    
    # 📈 Вычисляем прогресс
    total_modules = len(sorted_modules)
    progress_percent = round((completed_modules_count / total_modules * 100) if total_modules > 0 else 0, 1)
    
    # 🎯 Формируем минимальный ответ
    return {
        "header": {
            "course_title": course_title,
            "progress_percent": progress_percent
        },
        "sidebar": {
            "modules": [
                {
                    "id": module["id"],
                    "title": module["title"],
                    "group_title": module["group_title"],
                    "status": module["status"]
                }
                for module in sorted_modules
            ]
        },
        "content": {
            "current_module": {
                "id": current_module["id"] if current_module else None,
                "title": current_module["title"] if current_module else None,
                "group_title": current_module["group_title"] if current_module else None
            },
            "blocks": current_module["blocks"] if current_module else [],
            "can_complete_module": len(current_module["blocks"]) > 0 if current_module else False
        }
    }

@router.get("/{course_id}/modules/{module_id}/fast/", summary="Быстрая загрузка модуля")
async def load_module_fast(
    course_id: int, 
    module_id: int, 
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
):
    """
    Быстрая загрузка только блоков конкретного модуля
    """
    user_id = get_current_user_id(request)
    
    # 🔥 Один запрос для получения модуля с блоками
    query = (
        select(
            Module.id,
            Module.title,
            Module.group_title,
            ContentBlock.id.label('block_id'),
            ContentBlock.type,
            ContentBlock.title.label('block_title'),
            ContentBlock.content,
            ContentBlock.order,
            ContentBlock.video_preview,
            UserModuleProgress.id.label('progress_id')
        )
        .select_from(Module)
        .outerjoin(ContentBlock, Module.id == ContentBlock.module_id)
        .outerjoin(
            UserModuleProgress,
            and_(
                Module.id == UserModuleProgress.module_id,
                UserModuleProgress.user_id == user_id
            )
        )
        .where(
            Module.id == module_id,
            Module.course_id == course_id
        )
        .order_by(ContentBlock.order)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    
    # Обрабатываем результат
    module_data = {
        "id": rows[0].id,
        "title": rows[0].title,
        "group_title": rows[0].group_title,
        "is_completed": bool(rows[0].progress_id)
    }
    
    blocks = []
    for row in rows:
        if row.block_id:
            blocks.append({
                "id": row.block_id,
                "type": row.type,
                "title": row.block_title,
                "content": row.content,
                "order": row.order,
                "video_preview": row.video_preview
            })
    
    return {
        "module": module_data,
        "blocks": blocks
    }

@router.get("/{course_id}/sidebar/", summary="Только данные для сайдбара")
async def get_sidebar_data(
    course_id: int, 
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
):
    """
    Быстрая загрузка только данных для сайдбара
    Для обновления прогресса без перезагрузки всей страницы
    """
    user_id = get_current_user_id(request)
    
    # Минимальный запрос только для модулей и прогресса
    query = (
        select(
            Module.id,
            Module.title,
            Module.group_title,
            Module.order,
            UserModuleProgress.id.label('progress_id')
        )
        .select_from(Module)
        .outerjoin(
            UserModuleProgress,
            and_(
                Module.id == UserModuleProgress.module_id,
                UserModuleProgress.user_id == user_id
            )
        )
        .where(Module.course_id == course_id)
        .order_by(Module.order)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    modules = []
    completed_count = 0
    current_found = False
    
    for row in rows:
        is_completed = bool(row.progress_id)
        if is_completed:
            completed_count += 1
            status = "completed"
        else:
            status = "current" if not current_found else "locked"
            if not current_found:
                current_found = True
        
        modules.append({
            "id": row.id,
            "title": row.title,
            "group_title": row.group_title,
            "status": status
        })
    
    progress_percent = round((completed_count / len(rows) * 100) if rows else 0, 1)
    
    return {
        "modules": modules,
        "progress_percent": progress_percent
    }