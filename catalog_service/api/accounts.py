# catalog_service/api/accounts.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime

from db.dependencies import get_db_session
from models.course import Course
from models.access import CourseAccess
from catalog_service.models.module import Module
from catalog_service.models.progress import UserModuleProgress
from utils.auth import get_current_user_id
from schemas.dashboard import UserDashboardSchema, UserStatsSchema, UserCourseSchema
from schemas.progress import CourseProgressSchema
from utils.auth_client import get_user_data_from_auth

router = APIRouter()

@router.get("/dashboard/", response_model=UserDashboardSchema, summary="Пользовательский dashboard")
async def get_user_dashboard(request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Возвращает данные для пользовательского dashboard:
    - Статистику по курсам
    - Список купленных курсов с прогрессом
    - Недавнюю активность
    """
    user_id = get_current_user_id(request)
    
    # Получаем все курсы пользователя
    courses_result = await db.execute(
        select(CourseAccess, Course)
        .join(Course, CourseAccess.course_id == Course.id)
        .where(CourseAccess.user_id == user_id)
        .order_by(CourseAccess.purchased_at.desc())
    )
    user_courses_data = courses_result.all()
    
    if not user_courses_data:
        # Пользователь не купил ни одного курса
        return UserDashboardSchema(
            user_id=user_id,
            stats=UserStatsSchema(
                total_courses=0,
                completed_courses=0,
                total_progress_percent=0.0
            ),
            courses=[],
            recent_progress=[]
        )
    
    # Собираем данные по курсам и прогрессу
    courses_list = []
    progress_list = []
    completed_courses = 0
    total_progress = 0
    
    for access, course in user_courses_data:
        # Получаем общее количество модулей в курсе
        total_modules_result = await db.execute(
            select(func.count(Module.id)).where(Module.course_id == course.id)
        )
        total_modules = total_modules_result.scalar() or 0
        
        # Получаем количество завершенных модулей пользователем
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
        completed_modules = completed_modules_result.scalar() or 0
        
        # Вычисляем прогресс
        progress_percent = round((completed_modules / total_modules * 100) if total_modules > 0 else 0, 1)
        is_completed = progress_percent >= 100
        
        if is_completed:
            completed_courses += 1
        
        total_progress += progress_percent
        
        # Добавляем в список курсов
        courses_list.append(UserCourseSchema(
            course_id=course.id,
            course_title=course.title,
            image=course.image,
            purchased_at=access.purchased_at,
            progress_percent=progress_percent,
            is_completed=is_completed
        ))
        
        # Добавляем в список прогресса
        progress_list.append(CourseProgressSchema(
            course_id=course.id,
            course_title=course.title,
            total_modules=total_modules,
            completed_modules=completed_modules,
            progress_percent=progress_percent
        ))
    
    # Вычисляем общую статистику
    total_courses = len(user_courses_data)
    avg_progress = round(total_progress / total_courses if total_courses > 0 else 0, 1)
    
    # Берем только последние 5 курсов для recent_progress
    recent_progress = progress_list[:5]
    
    return UserDashboardSchema(
        user_id=user_id,
        stats=UserStatsSchema(
            total_courses=total_courses,
            completed_courses=completed_courses,
            total_progress_percent=avg_progress
        ),
        courses=courses_list,
        recent_progress=recent_progress
    )

@router.get("/my-courses/", response_model=List[CourseProgressSchema], summary="Мои курсы")
async def get_my_courses(request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Возвращает список всех курсов пользователя с прогрессом.
    Можно использовать для отдельной страницы "Мои курсы".
    """
    user_id = get_current_user_id(request)
    
    # Получаем все курсы пользователя
    result = await db.execute(
        select(CourseAccess).where(CourseAccess.user_id == user_id)
    )
    accesses = result.scalars().all()
    
    result_list = []
    
    for access in accesses:
        # Получаем информацию о курсе
        course_result = await db.execute(
            select(Course).where(Course.id == access.course_id)
        )
        course = course_result.scalar_one_or_none()
        if not course:
            continue
            
        # Получаем все модули курса
        modules_result = await db.execute(
            select(Module).where(Module.course_id == course.id)
        )
        modules = modules_result.scalars().all()
        total_modules = len(modules)
        module_ids = [m.id for m in modules]

        # Считаем завершенные модули
        completed_result = await db.execute(
            select(func.count(UserModuleProgress.id)).where(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id.in_(module_ids) if module_ids else False
            )
        )
        completed_count = completed_result.scalar() or 0

        percent = round(completed_count / total_modules * 100, 1) if total_modules > 0 else 0

        result_list.append(CourseProgressSchema(
            course_id=course.id,
            course_title=course.title,
            total_modules=total_modules,
            completed_modules=completed_count,
            progress_percent=percent
        ))

    return result_list

@router.get("/stats/", response_model=UserStatsSchema, summary="Статистика пользователя")
async def get_user_stats(request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Возвращает только статистику пользователя без детальных данных о курсах.
    Можно использовать для быстрой загрузки основных метрик.
    """
    user_id = get_current_user_id(request)
    
    # Считаем общее количество курсов
    total_courses_result = await db.execute(
        select(func.count(CourseAccess.id)).where(CourseAccess.user_id == user_id)
    )
    total_courses = total_courses_result.scalar() or 0
    
    if total_courses == 0:
        return UserStatsSchema(
            total_courses=0,
            completed_courses=0,
            total_progress_percent=0.0
        )
    
    # Получаем все курсы пользователя и их прогресс
    courses_result = await db.execute(
        select(CourseAccess.course_id).where(CourseAccess.user_id == user_id)
    )
    course_ids = [row[0] for row in courses_result.all()]
    
    completed_courses = 0
    total_progress = 0
    
    for course_id in course_ids:
        # Считаем модули в курсе
        total_modules_result = await db.execute(
            select(func.count(Module.id)).where(Module.course_id == course_id)
        )
        total_modules = total_modules_result.scalar() or 0
        
        if total_modules == 0:
            continue
            
        # Считаем завершенные модули
        completed_modules_result = await db.execute(
            select(func.count(UserModuleProgress.id))
            .select_from(
                UserModuleProgress.__table__.join(
                    Module.__table__,
                    UserModuleProgress.module_id == Module.id
                )
            )
            .where(
                Module.course_id == course_id,
                UserModuleProgress.user_id == user_id
            )
        )
        completed_modules = completed_modules_result.scalar() or 0
        
        progress_percent = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        if progress_percent >= 100:
            completed_courses += 1
            
        total_progress += progress_percent
    
    avg_progress = round(total_progress / total_courses if total_courses > 0 else 0, 1)
    
    return UserStatsSchema(
        total_courses=total_courses,
        completed_courses=completed_courses,
        total_progress_percent=avg_progress
    )
    

@router.get("/profile/", summary="Профиль пользователя")
async def get_user_profile(request: Request):
    """
    Возвращает данные пользователя из auth_service
    """
    user_id = get_current_user_id(request)
    
    # Получаем токен из заголовка Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Отсутствует токен авторизации"
        )
    
    access_token = auth_header.replace("Bearer ", "")
    
    # Запрашиваем данные пользователя из auth_service
    user_data = await get_user_data_from_auth(user_id, access_token)
    
    return user_data