from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone

from db.dependencies import get_db_session
from models.course import Course
from models.access import CourseAccess
from schemas.course import (
    CourseListSchema, CourseDetailSchema,
    CourseCreate, BuyCourseRequest, BuyCourseResponse,
)
from utils.auth import get_current_user_id
from utils.rate_limit import limiter

router = APIRouter(prefix="/courses")

def get_discount_info(course: Course):
    now = datetime.now(timezone.utc)
    is_active = (
        course.discount and float(course.discount) > 0 and
        course.discount_start and course.discount_until and
        course.discount_start <= now < course.discount_until
    )
    ends_in = ((course.discount_until - now).total_seconds() if is_active else None)
    return is_active, ends_in

@router.get("/", response_model=List[CourseListSchema], summary="Список всех курсов")
async def list_courses(request: Request, db: AsyncSession = Depends(get_db_session)):
    # user_id не обязателен для публичного списка
    try:
        user_id = get_current_user_id(request)
    except:
        user_id = None

    result = await db.execute(select(Course).order_by(Course.order.asc()))
    courses = result.scalars().all()
    out: List[CourseListSchema] = []

    for course in courses:
        is_discount_active, _ = get_discount_info(course)
        final_price = float(course.price or 0.0)
        if is_discount_active:
            final_price = final_price * (1 - float(course.discount or 0) / 100)

        if course.is_free:
            has_access = True
        elif user_id:
            acc_res = await db.execute(
                select(CourseAccess).where(
                    CourseAccess.user_id == user_id,
                    CourseAccess.course_id == course.id
                )
            )
            has_access = acc_res.scalar_one_or_none() is not None
        else:
            has_access = False

        out.append(CourseListSchema(
            id=course.id,
            title=course.title,
            short_description=course.short_description,
            image=course.image,
            is_free=course.is_free,
            price=float(course.price or 0.0),
            discount=float(course.discount or 0.0),
            final_price=round(final_price, 2),
            has_access=has_access,
            button_text="ОТКРЫТЬ",
            order=course.order,
            is_discount_active=is_discount_active,
        ))
    return out

@router.get("/{course_id}/", response_model=CourseDetailSchema, summary="Детали курса")
async def course_detail(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    try:
        user_id = get_current_user_id(request)
    except:
        user_id = None

    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    is_discount_active, discount_ends_in = get_discount_info(course)
    final_price = float(course.price or 0.0)
    if is_discount_active:
        final_price = final_price * (1 - float(course.discount or 0) / 100)

    if course.is_free:
        has_access = True
    elif user_id:
        acc_res = await db.execute(
            select(CourseAccess).where(
                CourseAccess.user_id == user_id,
                CourseAccess.course_id == course.id
            )
        )
        has_access = acc_res.scalar_one_or_none() is not None
    else:
        has_access = False

    return CourseDetailSchema(
        id=course.id,
        title=course.title,
        full_description=course.full_description,
        short_description=course.short_description,
        image=course.image,
        is_free=course.is_free,
        price=float(course.price or 0.0),
        discount=float(course.discount or 0.0),
        final_price=round(final_price, 2),
        has_access=has_access,
        button_text=("ОТКРЫТЬ" if has_access else "ПЕРЕЙТИ К ОПЛАТЕ"),
        video=course.video,
        video_preview=course.video_preview,
        banner_text=course.banner_text,
        banner_color_left=course.banner_color_left,
        banner_color_right=course.banner_color_right,
        order=course.order,
        is_discount_active=is_discount_active,
        discount_ends_in=discount_ends_in,
    )

@router.post("/{course_id}/buy/", response_model=BuyCourseResponse, summary="Приобрести курс")
@limiter.limit("3/minute")
async def buy_course(course_id: int, request_data: BuyCourseRequest, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)

    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    acc_res = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    if acc_res.scalar_one_or_none():
        return BuyCourseResponse(success=True, message="Курс уже доступен")

    # Для MVP выдаём доступ сразу и на платные тоже (платёжка позже)
    db.add(CourseAccess(user_id=user_id, course_id=course_id))
    await db.commit()

    return BuyCourseResponse(
        success=True,
        message=("Бесплатный курс успешно открыт" if course.is_free else "Курс успешно приобретён")
    )

@router.post("/{course_id}/check-access/", summary="Проверка доступа (deprecated)")
async def check_course_access(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    try:
        user_id = get_current_user_id(request)
    except:
        return {"has_access": False, "requires_auth": True, "message": "Необходима регистрация"}

    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    if course.is_free:
        return {"has_access": True, "requires_auth": False, "course_type": "free"}

    acc_res = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    has_access = acc_res.scalar_one_or_none() is not None
    return {"has_access": has_access, "requires_auth": False, "course_type": "paid"}
