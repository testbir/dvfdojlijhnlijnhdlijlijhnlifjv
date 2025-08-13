# catalog_service/api/internal.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, extract, select
from datetime import datetime, timedelta
from typing import List, Dict
from db.dependencies import get_db_session
from models.course import Course
from models.access import CourseAccess

router = APIRouter(prefix="/internal", tags=["Internal"])

# === СТАТИСТИКА ===

@router.get("/statistics/courses/", summary="Статистика по курсам")
async def get_courses_statistics(db: AsyncSession = Depends(get_db_session)):
    # Общее количество курсов
    total_result = await db.execute(select(func.count(Course.id)))
    total = total_result.scalar()
    
    # Бесплатные курсы
    free_result = await db.execute(
        select(func.count(Course.id)).where(Course.is_free == True)
    )
    free = free_result.scalar()
    
    # Платные курсы
    paid_result = await db.execute(
        select(func.count(Course.id)).where(Course.is_free == False)
    )
    paid = paid_result.scalar()
    
    return {
        "total": total,
        "free": free,
        "paid": paid
    }

@router.get("/statistics/revenue/", summary="Статистика доходов")
async def get_revenue_statistics(db: AsyncSession = Depends(get_db_session)):
    # Считаем общую выручку от платных курсов
    result = await db.execute(
        select(func.sum(Course.price * (1 - Course.discount / 100)))
        .select_from(
            Course.__table__.join(
                CourseAccess.__table__, 
                Course.id == CourseAccess.course_id
            )
        )
        .where(Course.is_free == False)
    )
    revenue = result.scalar()
    
    return {
        "total": float(revenue) if revenue else 0.0
    }



@router.get("/statistics/revenue-by-month/", summary="Доходы по месяцам")
async def get_revenue_by_month(months: int = 12, db: AsyncSession = Depends(get_db_session)):
    # Доходы за последние N месяцев
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    result = await db.execute(
        select(
            extract('year', CourseAccess.purchased_at).label('year'),
            extract('month', CourseAccess.purchased_at).label('month'),
            func.sum(Course.price * (1 - Course.discount / 100)).label('revenue')
        )
        .select_from(
            CourseAccess.__table__.join(
                Course.__table__,
                CourseAccess.course_id == Course.id
            )
        )
        .where(
            CourseAccess.purchased_at >= start_date,
            Course.is_free == False
        )
        .group_by(
            extract('year', CourseAccess.purchased_at),
            extract('month', CourseAccess.purchased_at)
        )
        .order_by(
            extract('year', CourseAccess.purchased_at),
            extract('month', CourseAccess.purchased_at)
        )
    )
    revenue_data = result.all()
    
    result_list = []
    for year, month, revenue in revenue_data:
        result_list.append({
            "month": f"{int(year)}-{int(month):02d}",
            "revenue": float(revenue) if revenue else 0.0
        })
    
    return result_list


@router.get("/statistics/recent-purchases/", summary="Последние покупки")
async def get_recent_purchases(limit: int = 10, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(
            CourseAccess.user_id,
            CourseAccess.purchased_at,
            Course.title,
            Course.price,
            Course.discount
        )
        .select_from(
            CourseAccess.__table__.join(
                Course.__table__,
                CourseAccess.course_id == Course.id
            )
        )
        .where(Course.is_free == False)
        .order_by(CourseAccess.purchased_at.desc())
        .limit(limit)
    )
    purchases = result.all()
    
    return [
        {
            "user_id": p.user_id,
            "purchased_at": p.purchased_at.isoformat(),
            "course_title": p.title,
            "amount": float(p.price * (1 - p.discount / 100))
        }
        for p in purchases
    ]

# === УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ===

@router.get("/users/{user_id}/courses/", summary="Курсы пользователя")
async def get_user_courses(user_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(
            Course.id.label('course_id'),
            Course.title.label('course_title'),
            CourseAccess.purchased_at
        )
        .select_from(
            Course.__table__.join(
                CourseAccess.__table__,
                Course.id == CourseAccess.course_id
            )
        )
        .where(CourseAccess.user_id == user_id)
    )
    courses = result.all()
    
    return {
        "courses": [
            {
                "course_id": c.course_id,
                "course_title": c.course_title,
                "purchased_at": c.purchased_at.isoformat()
            }
            for c in courses
        ]
    }
# === МАССОВЫЕ ОПЕРАЦИИ ===


@router.patch("/courses/{course_id}/discount", summary="Применить скидку к курсу")
async def apply_course_discount(
    course_id: int,
    discount: float = Body(..., embed=True),
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    if not 0 <= discount <= 100:
        raise HTTPException(status_code=400, detail="Скидка должна быть от 0 до 100")
    
    course.discount = discount
    await db.commit()
    
    return {"success": True, "discount": discount}

@router.patch("/courses/{course_id}/order", summary="Изменить порядок курса")  
async def update_course_order(
    course_id: int,
    order: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    course.order = order
    await db.commit()
    
    return {"success": True, "order": order}