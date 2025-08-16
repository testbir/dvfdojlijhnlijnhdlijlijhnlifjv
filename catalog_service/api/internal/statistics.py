# catalog_service/api/internal/statistics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from datetime import datetime, timedelta

from db.dependencies import get_db_session
from models.course import Course
from models.access import CourseAccess

router = APIRouter(prefix="/statistics")

@router.get("/courses", summary="Статистика по курсам")
async def stats_courses(db: AsyncSession = Depends(get_db_session)):
    total = (await db.execute(select(func.count(Course.id)))).scalar()
    free  = (await db.execute(select(func.count(Course.id)).where(Course.is_free == True))).scalar()
    paid  = (await db.execute(select(func.count(Course.id)).where(Course.is_free == False))).scalar()
    return {"total": total, "free": free, "paid": paid}

@router.get("/revenue", summary="Статистика доходов")
async def stats_revenue(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(
        select(func.sum(func.coalesce(Course.price, 0) * (1 - func.coalesce(Course.discount, 0) / 100)))
        .select_from(Course.__table__.join(CourseAccess.__table__, Course.id == CourseAccess.course_id))
        .where(Course.is_free == False)
    )
    revenue = res.scalar()
    return {"total": float(revenue) if revenue else 0.0}

@router.get("/revenue-by-month", summary="Доходы по месяцам")
async def stats_revenue_by_month(months: int = 12, db: AsyncSession = Depends(get_db_session)):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    res = await db.execute(
        select(
            extract('year', CourseAccess.purchased_at).label('year'),
            extract('month', CourseAccess.purchased_at).label('month'),
            func.sum(func.coalesce(Course.price, 0) * (1 - func.coalesce(Course.discount, 0) / 100)).label('revenue')
        )
        .select_from(CourseAccess.__table__.join(Course.__table__, CourseAccess.course_id == Course.id))
        .where(CourseAccess.purchased_at >= start_date, Course.is_free == False)
        .group_by(extract('year', CourseAccess.purchased_at), extract('month', CourseAccess.purchased_at))
        .order_by(extract('year', CourseAccess.purchased_at), extract('month', CourseAccess.purchased_at))
    )
    rows = res.all()
    return [{"month": f"{int(y)}-{int(m):02d}", "revenue": float(r or 0.0)} for y, m, r in rows]

@router.get("/courses/{course_id}", summary="Статистика по курсу")
async def stats_course(course_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    enrollments = (await db.execute(select(func.count(CourseAccess.id)).where(CourseAccess.course_id == course_id))).scalar()
    revenue = 0.0 if course.is_free else float((course.price or 0) * (1 - (course.discount or 0)/100) * (enrollments or 0))
    return {
        "course_id": course_id,
        "title": course.title,
        "enrollments": enrollments or 0,
        "total_modules": 0,
        "average_completion": 0.0,
        "revenue": revenue,
        "is_free": course.is_free
    }

@router.get("/recent-purchases", summary="Последние покупки")
async def stats_recent_purchases(limit: int = 10, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(
        select(CourseAccess.user_id, CourseAccess.purchased_at, Course.title, Course.price, Course.discount)
        .select_from(CourseAccess.__table__.join(Course.__table__, CourseAccess.course_id == Course.id))
        .where(Course.is_free == False)
        .order_by(CourseAccess.purchased_at.desc())
        .limit(limit)
    )
    rows = res.all()
    return [
        {
            "user_id": r.user_id,
            "purchased_at": r.purchased_at.isoformat(),
            "course_title": r.title,
            "amount": float((r.price or 0) * (1 - (r.discount or 0)/100))
        } for r in rows
    ]

@router.get("/popular-courses", summary="Популярные курсы")
async def stats_popular(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(
        select(Course.id, Course.title, func.count(CourseAccess.id).label('enrollments'))
        .select_from(Course.__table__.join(CourseAccess.__table__, Course.id == CourseAccess.course_id))
        .group_by(Course.id, Course.title)
        .order_by(func.count(CourseAccess.id).desc())
        .limit(5)
    )
    rows = res.all()
    return [
        {"id": cid, "title": title, "enrollments": enr, "completion_rate": 0.0}
        for cid, title, enr in rows
    ]
