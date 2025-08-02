# catalog_service/api/course_modal.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from db.dependencies import get_db_session
from models.course_modal import CourseModal, CourseModalBlock
from models.course import Course
from schemas.course_modal import (
    CourseModalCreate, 
    CourseModalUpdate, 
    CourseModalSchema,
    CourseModalBlockSchema
)

router = APIRouter(prefix="/internal/course-modals", tags=["Course Modals"])

@router.get("/course/{course_id}/", response_model=Optional[CourseModalSchema])
async def get_course_modal(course_id: int, db: AsyncSession = Depends(get_db_session)):
    """Получить модальное окно для курса"""
    # Проверяем существование курса
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Получаем модальное окно
    result = await db.execute(
        select(CourseModal).where(CourseModal.course_id == course_id)
    )
    modal = result.scalar_one_or_none()
    
    if not modal:
        return None
    
    # Получаем блоки
    blocks_result = await db.execute(
        select(CourseModalBlock)
        .where(CourseModalBlock.modal_id == modal.id)
        .order_by(CourseModalBlock.order)
    )
    blocks = blocks_result.scalars().all()
    
    return CourseModalSchema(
        id=modal.id,
        course_id=modal.course_id,
        title=modal.title,
        blocks=[CourseModalBlockSchema.from_orm(block) for block in blocks]
    )

@router.post("/course/{course_id}/", response_model=CourseModalSchema)
async def create_course_modal(
    course_id: int, 
    data: CourseModalCreate, 
    db: AsyncSession = Depends(get_db_session)
):
    """Создать модальное окно для курса"""
    # Проверяем существование курса
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Проверяем, нет ли уже модального окна
    existing_result = await db.execute(
        select(CourseModal).where(CourseModal.course_id == course_id)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Модальное окно для этого курса уже существует")
    
    # Создаем модальное окно
    modal = CourseModal(course_id=course_id, title=data.title)
    db.add(modal)
    await db.commit()
    await db.refresh(modal)
    
    # Создаем блоки
    blocks = []
    for block_data in data.blocks:
        block = CourseModalBlock(
            modal_id=modal.id,
            type=block_data.type,
            content=block_data.content,
            order=block_data.order
        )
        db.add(block)
        blocks.append(block)
    
    await db.commit()
    
    return CourseModalSchema(
        id=modal.id,
        course_id=modal.course_id,
        title=modal.title,
        blocks=[CourseModalBlockSchema.from_orm(block) for block in blocks]
    )

@router.put("/course/{course_id}/", response_model=CourseModalSchema)
async def update_course_modal(
    course_id: int, 
    data: CourseModalUpdate, 
    db: AsyncSession = Depends(get_db_session)
):
    """Обновить модальное окно курса"""
    # Получаем существующее модальное окно
    result = await db.execute(
        select(CourseModal).where(CourseModal.course_id == course_id)
    )
    modal = result.scalar_one_or_none()
    if not modal:
        raise HTTPException(status_code=404, detail="Модальное окно не найдено")
    
    # Обновляем заголовок
    if data.title is not None:
        modal.title = data.title
    
    # Обновляем блоки
    if data.blocks is not None:
        # Удаляем старые блоки
        await db.execute(
            select(CourseModalBlock).where(CourseModalBlock.modal_id == modal.id)
        )
        old_blocks_result = await db.execute(
            select(CourseModalBlock).where(CourseModalBlock.modal_id == modal.id)
        )
        old_blocks = old_blocks_result.scalars().all()
        for block in old_blocks:
            await db.delete(block)
        
        # Создаем новые блоки
        for block_data in data.blocks:
            block = CourseModalBlock(
                modal_id=modal.id,
                type=block_data.type,
                content=block_data.content,
                order=block_data.order
            )
            db.add(block)
    
    await db.commit()
    await db.refresh(modal)
    
    # Получаем обновленные блоки
    blocks_result = await db.execute(
        select(CourseModalBlock)
        .where(CourseModalBlock.modal_id == modal.id)
        .order_by(CourseModalBlock.order)
    )
    blocks = blocks_result.scalars().all()
    
    return CourseModalSchema(
        id=modal.id,
        course_id=modal.course_id,
        title=modal.title,
        blocks=[CourseModalBlockSchema.from_orm(block) for block in blocks]
    )

@router.delete("/course/{course_id}/")
async def delete_course_modal(course_id: int, db: AsyncSession = Depends(get_db_session)):
    """Удалить модальное окно курса"""
    result = await db.execute(
        select(CourseModal).where(CourseModal.course_id == course_id)
    )
    modal = result.scalar_one_or_none()
    if not modal:
        raise HTTPException(status_code=404, detail="Модальное окно не найдено")
    
    await db.delete(modal)
    await db.commit()
    
    return {"message": "Модальное окно удалено"}