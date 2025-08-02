# catalog_service/api/module.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.dependencies import get_db_session
from models.course import Course
from models.module import Module
from models.content import ContentBlock
from schemas.module import ModuleCreate, ModuleSchema, ModuleShortSchema, ModuleContentSchema
from schemas.block import BlockOrderUpdate
from schemas.block import ContentBlockCreateSchema

router = APIRouter()

@router.post("/internal/courses/{course_id}/modules/", summary="создание модуля (admin)")
async def admin_create_module(course_id: int, data: ModuleCreate, db: AsyncSession = Depends(get_db_session)):
    # Проверяем существование курса
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    module = Module(course_id=course_id, **data.dict())
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return {"id": module.id, "message": "Модуль создан"}

@router.post("/internal/modules/{module_id}/blocks/", summary="Создание контент-блока в модуле (admin)")
async def admin_create_block(module_id: int, data: ContentBlockCreateSchema, db: AsyncSession = Depends(get_db_session)):
    # Проверяем существование модуля
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")
        
    if data.type not in ["text", "video", "code", "image"]:
        raise HTTPException(status_code=400, detail="Недопустимый тип контента")
        
    block = ContentBlock(module_id=module_id, **data.dict())
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return {"id": block.id, "message": "Контент-блок создан"}

@router.put("/internal/modules/{module_id}", summary="Обновление модуля (admin)")
async def admin_update_module(module_id: int, data: ModuleCreate, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")

    for key, value in data.dict().items():
        setattr(module, key, value)

    await db.commit()
    await db.refresh(module)
    return {"id": module.id, "message": "Модуль обновлён"}

@router.get("/internal/modules/{module_id}/blocks/", summary="Получение всех блоков модуля (admin)")
async def admin_get_blocks(module_id: int, db: AsyncSession = Depends(get_db_session)):
    # Проверяем существование модуля
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    
    # Получаем блоки модуля
    result = await db.execute(
        select(ContentBlock)
        .where(ContentBlock.module_id == module_id)
        .order_by(ContentBlock.order)
    )
    blocks = result.scalars().all()
    
    return [
        {
            "id": block.id,
            "type": block.type,
            "order": block.order,
            "content": block.content
        }
        for block in blocks
    ]

@router.put("/internal/modules/{module_id}/blocks/order/", summary="Обновление порядка блоков модуля (admin)")
async def update_blocks_order(module_id: int, blocks: List[BlockOrderUpdate], db: AsyncSession = Depends(get_db_session)):
    for block_data in blocks:
        # Получаем блок и проверяем его принадлежность модулю
        result = await db.execute(
            select(ContentBlock).where(
                ContentBlock.id == block_data.block_id,
                ContentBlock.module_id == module_id
            )
        )
        block = result.scalar_one_or_none()
        if not block:
            raise HTTPException(status_code=404, detail=f"Блок {block_data.block_id} не найден в модуле {module_id}")

        block.order = block_data.order

    await db.commit()
    return {"message": "Порядок блоков обновлён"}

@router.get("/internal/modules/{module_id}", summary="Получение данных модуля по ID (admin)")
async def get_module_by_id(module_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    return {
        "id": module.id,
        "title": module.title,
        "group_title": module.group_title,
        "order": module.order,
        "course_id": module.course_id
    }

@router.delete("/internal/modules/{module_id}", summary="Удаление модуля (admin)")
async def admin_delete_module(module_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")

    await db.delete(module)
    await db.commit()
    return {"message": "Модуль удалён"}

@router.get("/{course_id}/modules/", summary="Получение всех модулей курса (публично)")
async def get_modules_for_course(course_id: int, db: AsyncSession = Depends(get_db_session)):
    # Проверяем существование курса
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Получаем модули курса
    result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.order)
    )
    modules = result.scalars().all()
    
    return [
        {
            "id": module.id,
            "title": module.title,
            "order": module.order,
            "group_title": module.group_title
        }
        for module in modules
    ]