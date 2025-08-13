# catalog_service/crud/course.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.course import Course
from catalog_service.models.module import Module
from models.access import CourseAccess

async def get_course_structure(db: AsyncSession, course_id: int):
    result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.order)
    )
    modules = result.scalars().all()
    return modules

async def has_course_access(db: AsyncSession, user_id: int, course_id: int) -> bool:
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        return False
    if course.is_free:
        return True
    
    result = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    return result.scalar_one_or_none() is not None