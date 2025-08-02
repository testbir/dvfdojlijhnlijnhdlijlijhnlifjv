# admin_service/api/courses.py

from fastapi import APIRouter, HTTPException, Depends
from schemas import CourseCreate
from utils.auth import get_current_admin_user
from models.admin import AdminUser
from services.catalog_api import (
    get_courses,
    get_course_internal as get_course,
    create_course,
    update_course,
    delete_course
)
import logging

router = APIRouter(prefix="/admin/courses", tags=["Admin Courses"])
logger = logging.getLogger(__name__)


@router.get("/", summary="Получить список курсов")
async def list_courses(current_admin: AdminUser = Depends(get_current_admin_user)):
    """Получает список всех курсов"""
    logger.info(f"Админ {current_admin.username} запрашивает список курсов")
    
    try:
        courses = await get_courses()
        return {"courses": courses}
    except Exception as e:
        logger.error(f"Ошибка получения списка курсов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения курсов: {str(e)}")


@router.post("/", summary="Создать новый курс")
async def create_course_route(
    data: CourseCreate,  
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создает новый курс"""
    logger.info(f"Админ {current_admin.username} создает курс: {data.title}")
    
    try:
        result = await create_course(data)
        logger.info(f"Курс успешно создан: {result}")
        return result
    except Exception as e:
        logger.error(f"Ошибка создания курса: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания курса: {str(e)}")


@router.get("/{course_id}", summary="Получить курс по ID")
async def retrieve_course(
    course_id: int,  
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получает детальную информацию о курсе"""
    logger.info(f"Админ {current_admin.username} запрашивает курс {course_id}")
    
    try:
        return await get_course(course_id)
    except Exception as e:
        logger.error(f"Ошибка получения курса {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения курса: {str(e)}")


@router.put("/{course_id}", summary="Обновить курс по ID")
async def edit_course(
    course_id: int, 
    data: CourseCreate,  
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновляет существующий курс"""
    logger.info(f"Админ {current_admin.username} обновляет курс {course_id}: {data.title}")
    
    try:
        result = await update_course(course_id, data)
        logger.info(f"Курс {course_id} успешно обновлен")
        return result
    except Exception as e:
        logger.error(f"Ошибка обновления курса {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления курса: {str(e)}")


@router.delete("/{course_id}", summary="Удалить курс по ID")
async def remove_course(
    course_id: int,  
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удаляет курс и все связанные данные"""
    logger.warning(f"Админ {current_admin.username} удаляет курс {course_id}")
    
    try:
        result = await delete_course(course_id)
        logger.info(f"Курс {course_id} успешно удален")
        return result
    except Exception as e:
        logger.error(f"Ошибка удаления курса {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления курса: {str(e)}")