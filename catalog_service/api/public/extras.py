
# catalog_service/api/public/extras.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from db.dependencies import get_db_session
from models.course_modal import CourseModal, CourseModalBlock
from models.student_works import StudentWorksSection, StudentWork
from models.course import Course

router = APIRouter(prefix="/courses", tags=["Public Course Extras"])







@router.get("/{course_id}/modal/", response_model=Optional[dict])
async def get_course_modal_public(
    course_id: int, 
    db: AsyncSession = Depends(get_db_session)
):
    """Получить модальное окно курса (публичный доступ)"""
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
    
    return {
        "title": modal.title,
        "blocks": [
            {
                "type": block.type,
                "content": block.content,
                "order": block.order
            }
            for block in blocks
        ]
    }

@router.get("/{course_id}/student-works/", response_model=Optional[dict])
async def get_student_works_public(
    course_id: int, 
    db: AsyncSession = Depends(get_db_session)
):
    """Получить работы учеников курса (публичный доступ)"""
    # Проверяем существование курса
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Получаем секцию работ
    result = await db.execute(
        select(StudentWorksSection).where(StudentWorksSection.course_id == course_id)
    )
    section = result.scalar_one_or_none()
    
    if not section:
        return None
    
    # Получаем работы
    works_result = await db.execute(
        select(StudentWork)
        .where(StudentWork.section_id == section.id)
        .order_by(StudentWork.order)
    )
    works = works_result.scalars().all()
    
    return {
        "title": section.title,
        "description": section.description,
        "works": [
            {
                "image": work.image,
                "description": work.description,
                "bot_tag": work.bot_tag,
                "order": work.order
            }
            for work in works
        ]
    }