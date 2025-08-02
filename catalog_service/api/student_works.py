# catalog_service/api/student_works.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from db.dependencies import get_db_session
from models.student_works import StudentWorksSection, StudentWork
from models.course import Course
from schemas.student_works import (
    StudentWorksSectionCreate,
    StudentWorksSectionUpdate,
    StudentWorksSectionSchema,
    StudentWorkSchema
)

router = APIRouter(prefix="/internal/student-works", tags=["Student Works"])

@router.get("/course/{course_id}/", response_model=Optional[StudentWorksSectionSchema])
async def get_student_works_section(course_id: int, db: AsyncSession = Depends(get_db_session)):
    """Получить секцию работ учеников для курса"""
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
    
    return StudentWorksSectionSchema(
        id=section.id,
        course_id=section.course_id,
        title=section.title,
        description=section.description,
        works=[StudentWorkSchema.from_orm(work) for work in works]
    )

@router.post("/course/{course_id}/", response_model=StudentWorksSectionSchema)
async def create_student_works_section(
    course_id: int,
    data: StudentWorksSectionCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Создать секцию работ учеников для курса"""
    # Проверяем существование курса
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Проверяем, нет ли уже секции
    existing_result = await db.execute(
        select(StudentWorksSection).where(StudentWorksSection.course_id == course_id)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Секция работ для этого курса уже существует")
    
    # Создаем секцию
    section = StudentWorksSection(
        course_id=course_id,
        title=data.title,
        description=data.description
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)
    
    # Создаем работы
    works = []
    for work_data in data.works:
        work = StudentWork(
            section_id=section.id,
            image=work_data.image,
            description=work_data.description,
            bot_tag=work_data.bot_tag,
            order=work_data.order
        )
        db.add(work)
        works.append(work)
    
    await db.commit()
    
    return StudentWorksSectionSchema(
        id=section.id,
        course_id=section.course_id,
        title=section.title,
        description=section.description,
        works=[StudentWorkSchema.from_orm(work) for work in works]
    )

@router.put("/course/{course_id}/", response_model=StudentWorksSectionSchema)
async def update_student_works_section(
    course_id: int,
    data: StudentWorksSectionUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Обновить секцию работ учеников"""
    # Получаем существующую секцию
    result = await db.execute(
        select(StudentWorksSection).where(StudentWorksSection.course_id == course_id)
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Секция работ не найдена")
    
    # Обновляем данные секции
    if data.title is not None:
        section.title = data.title
    if data.description is not None:
        section.description = data.description
    
    # Обновляем работы
    if data.works is not None:
        # Удаляем старые работы
        old_works_result = await db.execute(
            select(StudentWork).where(StudentWork.section_id == section.id)
        )
        old_works = old_works_result.scalars().all()
        for work in old_works:
            await db.delete(work)
        
        # Создаем новые работы
        for work_data in data.works:
            work = StudentWork(
                section_id=section.id,
                image=work_data.image,
                description=work_data.description,
                bot_tag=work_data.bot_tag,
                order=work_data.order
            )
            db.add(work)
    
    await db.commit()
    await db.refresh(section)
    
    # Получаем обновленные работы
    works_result = await db.execute(
        select(StudentWork)
        .where(StudentWork.section_id == section.id)
        .order_by(StudentWork.order)
    )
    works = works_result.scalars().all()
    
    return StudentWorksSectionSchema(
        id=section.id,
        course_id=section.course_id,
        title=section.title,
        description=section.description,
        works=[StudentWorkSchema.from_orm(work) for work in works]
    )

@router.delete("/course/{course_id}/")
async def delete_student_works_section(course_id: int, db: AsyncSession = Depends(get_db_session)):
    """Удалить секцию работ учеников"""
    result = await db.execute(
        select(StudentWorksSection).where(StudentWorksSection.course_id == course_id)
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Секция работ не найдена")
    
    await db.delete(section)
    await db.commit()
    
    return {"message": "Секция работ удалена"}