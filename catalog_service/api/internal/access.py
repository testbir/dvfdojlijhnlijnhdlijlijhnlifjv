# catalog_service/api/internal/access.py


from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.dependencies import get_db_session
from models.course import Course
from models.access import CourseAccess

router = APIRouter(prefix="/access")

@router.post("/verify", summary="Проверка доступа")
async def access_verify(payload: dict = Body(...), db: AsyncSession = Depends(get_db_session)):
    user_id = int(payload.get("user_id"))
    course_id = int(payload.get("course_id"))

    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    if course.is_free:
        return {"has_access": True}

    acc_res = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    return {"has_access": acc_res.scalar_one_or_none() is not None}

@router.post("/enrollment/events", summary="Событие доступа (grant|revoke)")
async def enrollment_event(payload: dict = Body(...)):
    return {"accepted": True}
