# catalog_service/api/internal.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, extract, select
from datetime import datetime, timedelta
from typing import List, Dict
from db.dependencies import get_db_session
from models.course import Course
from models.access import CourseAccess
from catalog_service.models.module import Module
from catalog_service.models.progress import UserModuleProgress

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

@router.get("/statistics/popular-courses/", summary="Популярные курсы")
async def get_popular_courses(db: AsyncSession = Depends(get_db_session)):
    # Топ-5 курсов по количеству покупок
    result = await db.execute(
        select(
            Course.id,
            Course.title,
            func.count(CourseAccess.id).label('enrollments')
        )
        .select_from(
            Course.__table__.join(
                CourseAccess.__table__, 
                Course.id == CourseAccess.course_id
            )
        )
        .group_by(Course.id, Course.title)
        .order_by(func.count(CourseAccess.id).desc())
        .limit(5)
    )
    popular = result.all()
    
    result_list = []
    for course_id, title, enrollments in popular:
        # Считаем процент завершения
        total_modules_result = await db.execute(
            select(func.count(Module.id)).where(Module.course_id == course_id)
        )
        total_modules = total_modules_result.scalar()
        
        if total_modules > 0:
            # Считаем средний прогресс по курсу
            avg_progress_result = await db.execute(
                select(func.avg(
                    func.count(UserModuleProgress.id) * 100.0 / total_modules
                ))
                .select_from(
                    UserModuleProgress.__table__.join(
                        Module.__table__,
                        UserModuleProgress.module_id == Module.id
                    )
                )
                .where(Module.course_id == course_id)
                .group_by(UserModuleProgress.user_id)
            )
            completion_rate = avg_progress_result.scalar() or 0
        else:
            completion_rate = 0
            
        result_list.append({
            "id": course_id,
            "title": title,
            "enrollments": enrollments,
            "completion_rate": round(float(completion_rate), 1)
        })
    
    return result_list

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

@router.get("/statistics/courses/{course_id}/", summary="Статистика по курсу")
async def get_course_statistics(course_id: int, db: AsyncSession = Depends(get_db_session)):
    # Проверяем существование курса
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Количество студентов
    enrollments_result = await db.execute(
        select(func.count(CourseAccess.id)).where(CourseAccess.course_id == course_id)
    )
    enrollments = enrollments_result.scalar()
    
    # Количество модулей
    total_modules_result = await db.execute(
        select(func.count(Module.id)).where(Module.course_id == course_id)
    )
    total_modules = total_modules_result.scalar()
    
    # Средний прогресс
    if total_modules > 0 and enrollments > 0:
        completion_stats_result = await db.execute(
            select(
                UserModuleProgress.user_id,
                func.count(UserModuleProgress.id).label('completed')
            )
            .select_from(
                UserModuleProgress.__table__.join(
                    Module.__table__,
                    UserModuleProgress.module_id == Module.id
                )
            )
            .where(Module.course_id == course_id)
            .group_by(UserModuleProgress.user_id)
        )
        completion_stats = completion_stats_result.all()
        
        if completion_stats:
            avg_completion = sum(stat.completed for stat in completion_stats) / (len(completion_stats) * total_modules) * 100
        else:
            avg_completion = 0
    else:
        avg_completion = 0
    
    # Доход от курса
    if not course.is_free:
        revenue = float(course.price * (1 - course.discount / 100) * enrollments)
    else:
        revenue = 0
    
    return {
        "course_id": course_id,
        "title": course.title,
        "enrollments": enrollments,
        "total_modules": total_modules,
        "average_completion": round(avg_completion, 1),
        "revenue": revenue,
        "is_free": course.is_free
    }

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

@router.get("/users/{user_id}/courses-count/", summary="Количество курсов пользователя")
async def get_user_courses_count(user_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(func.count(CourseAccess.id)).where(CourseAccess.user_id == user_id)
    )
    count = result.scalar()
    
    return {"count": count}

@router.post("/users/{user_id}/grant-access/", summary="Предоставить доступ к курсу")
async def grant_course_access(
    user_id: int,
    course_id: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_db_session)
):
    # Проверяем, существует ли курс
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Проверяем, нет ли уже доступа
    existing_result = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=409, detail="Доступ уже предоставлен")
    
    # Создаем доступ
    access = CourseAccess(
        user_id=user_id,
        course_id=course_id,
        purchased_at=datetime.utcnow()
    )
    db.add(access)
    await db.commit()
    
    return {"success": True}

@router.delete("/users/{user_id}/remove-access/{course_id}/", summary="Отозвать доступ к курсу")
async def remove_course_access(
    user_id: int,
    course_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    access = result.scalar_one_or_none()
    
    if not access:
        raise HTTPException(status_code=404, detail="Доступ не найден")
    
    await db.delete(access)
    await db.commit()
    
    return {"success": True}

@router.get("/users/{user_id}/progress/", summary="Прогресс пользователя")
async def get_user_progress(user_id: int, db: AsyncSession = Depends(get_db_session)):
    # Получаем все курсы пользователя с прогрессом
    courses_result = await db.execute(
        select(Course)
        .select_from(
            Course.__table__.join(
                CourseAccess.__table__,
                Course.id == CourseAccess.course_id
            )
        )
        .where(CourseAccess.user_id == user_id)
    )
    courses = courses_result.scalars().all()
    
    result = []
    for course in courses:
        # Общее количество модулей в курсе
        total_modules_result = await db.execute(
            select(func.count(Module.id)).where(Module.course_id == course.id)
        )
        total_modules = total_modules_result.scalar()
        
        # Завершенные модули пользователем
        completed_modules_result = await db.execute(
            select(func.count(UserModuleProgress.id))
            .select_from(
                UserModuleProgress.__table__.join(
                    Module.__table__,
                    UserModuleProgress.module_id == Module.id
                )
            )
            .where(
                Module.course_id == course.id,
                UserModuleProgress.user_id == user_id
            )
        )
        completed_modules = completed_modules_result.scalar()
        
        progress = round((completed_modules / total_modules * 100) if total_modules > 0 else 0, 1)
        
        result.append({
            "course_id": course.id,
            "course_title": course.title,
            "total_modules": total_modules,
            "completed_modules": completed_modules,
            "progress_percent": progress
        })
    
    return result

# === МАССОВЫЕ ОПЕРАЦИИ ===

@router.post("/courses/{course_id}/duplicate/", summary="Дублировать курс")
async def duplicate_course(course_id: int, db: AsyncSession = Depends(get_db_session)):
    # Находим оригинальный курс
    result = await db.execute(select(Course).where(Course.id == course_id))
    original = result.scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Создаем копию курса
    new_course = Course(
        title=f"{original.title} (копия)",
        short_description=original.short_description,
        full_description=original.full_description,
        image=original.image,
        is_free=original.is_free,
        price=original.price,
        discount=original.discount,
        video=original.video,
        video_preview=original.video_preview,
        banner_text=original.banner_text,
        banner_color_left=original.banner_color_left,
        banner_color_right=original.banner_color_right,
        group_title=original.group_title,
        order=original.order + 1
    )
    db.add(new_course)
    await db.flush()
    
    # Копируем модули
    modules_result = await db.execute(
        select(Module).where(Module.course_id == course_id)
    )
    modules = modules_result.scalars().all()
    
    for module in modules:
        new_module = Module(
            course_id=new_course.id,
            group_title=module.group_title,
            title=module.title,
            order=module.order
        )
        db.add(new_module)
        await db.flush()
        
        # Копируем блоки контента
        from catalog_service.models.content import ContentBlock
        blocks_result = await db.execute(
            select(ContentBlock).where(ContentBlock.module_id == module.id)
        )
        blocks = blocks_result.scalars().all()
        
        for block in blocks:
            new_block = ContentBlock(
                module_id=new_module.id,
                title=block.title,
                type=block.type,
                content=block.content,
                order=block.order,
                video_preview=block.video_preview
            )
            db.add(new_block)
    
    await db.commit()
    
    return {"id": new_course.id, "message": "Курс успешно дублирован"}

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