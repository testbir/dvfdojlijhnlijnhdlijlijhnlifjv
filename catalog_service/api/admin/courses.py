

# catalog_service/api/course.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.dependencies import get_db_session
from models.course import Course


from schemas.course import (
    CourseCreate,
)

from datetime import datetime, timezone
from utils.rate_limit import limiter
from typing import List

router = APIRouter()






@router.post("/courses/")
async def admin_create_course(data: CourseCreate, db: AsyncSession = Depends(get_db_session)):
    print(">> Принятые данные:", data.dict())
    course = Course(**data.model_dump(mode="python"))
    db.add(course)
    await db.commit()
    await db.refresh(course)
    
    return {"id": course.id, "message": "Курс создан"}


@router.put("/courses/{course_id}")
async def admin_update_course(course_id: int, data: CourseCreate, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    for key, value in data.model_dump(mode="python", exclude_unset=True).items():
        if isinstance(value, str) and not value.strip():
            value = None
        setattr(course, key, value)

    await db.commit()
    await db.refresh(course)
    return {"id": course.id, "message": "Курс обновлён"}


@router.delete("/courses/{course_id}")
async def admin_delete_course(course_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    await db.delete(course)
    await db.commit()
    return {"message": "Курс удалён"}

def get_discount_info(course: Course):

    now = datetime.now(timezone.utc)

    is_active = (
        course.discount and float(course.discount) > 0 and
        course.discount_start and course.discount_until and
        course.discount_start <= now < course.discount_until
    )
    ends_in = (
        (course.discount_until - now).total_seconds()
        if is_active else None
    )
    return is_active, ends_in


@router.get("/courses/{course_id}", response_model=CourseCreate)
async def admin_get_course(course_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course