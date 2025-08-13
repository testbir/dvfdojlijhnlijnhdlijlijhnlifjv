from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.dependencies import get_db_session
from models.course import Course
from models.access import CourseAccess

router = APIRouter()

@router.get("/users/{user_id}/courses", summary="Курсы пользователя")
async def get_user_courses(user_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(
        select(Course.id, Course.title, CourseAccess.purchased_at)
        .select_from(Course.__table__.join(CourseAccess.__table__, Course.id == CourseAccess.course_id))
        .where(CourseAccess.user_id == user_id)
    )
    items = res.all()
    return {"courses": [
        {"course_id": c.id, "course_title": c.title, "purchased_at": c.purchased_at.isoformat()} for c in items
    ]}

@router.get("/users/{user_id}/courses-count", summary="Кол-во курсов пользователя")
async def get_user_courses_count(user_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(func.count(CourseAccess.id)).where(CourseAccess.user_id == user_id))
    return {"count": res.scalar()}

@router.post("/users/{user_id}/grant-access", summary="Выдать доступ")
async def grant_course_access(user_id: int, course_id: int = Body(..., embed=True), db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Course).where(Course.id == course_id))
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Курс не найден")

    dup = await db.execute(
        select(CourseAccess).where(CourseAccess.user_id == user_id, CourseAccess.course_id == course_id)
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Доступ уже предоставлен")

    db.add(CourseAccess(user_id=user_id, course_id=course_id))
    await db.commit()
    return {"success": True}

@router.delete("/users/{user_id}/remove-access/{course_id}", summary="Отозвать доступ")
async def remove_course_access(user_id: int, course_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(
        select(CourseAccess).where(CourseAccess.user_id == user_id, CourseAccess.course_id == course_id)
    )
    access = res.scalar_one_or_none()
    if not access:
        raise HTTPException(status_code=404, detail="Доступ не найден")
    await db.delete(access)
    await db.commit()
    return {"success": True}
