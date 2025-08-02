# admin_service/api/courses.py

from fastapi import APIRouter, HTTPException
from schemas import CourseCreate
from utils.auth import get_current_user
from fastapi import Depends
from services.catalog_api import (
    get_courses,
    get_course_internal as get_course,
    create_course,
    update_course,
    delete_course
)

router = APIRouter(prefix="/admin/courses", tags=["Admin Courses"])


@router.get("/", summary="Получить список курсов")
async def list_courses(user_id: str = Depends(get_current_user)):
    courses = await get_courses()
    return {"courses": courses}


@router.post("/", summary="Создать новый курс")
async def create_course_route(data: CourseCreate,  user_id: str = Depends(get_current_user)):
    result = await create_course(data)
    return result



@router.get("/{course_id}", summary="Получить курс по ID")
async def retrieve_course(course_id: int,  user_id: str = Depends(get_current_user)):
    return await get_course(course_id)


@router.put("/{course_id}", summary="Обновить курс по ID")
async def edit_course(course_id: int, data: CourseCreate,  user_id: str = Depends(get_current_user)):
    return await update_course(course_id, data)



@router.delete("/{course_id}", summary="Удалить курс по ID")
async def remove_course(course_id: int,  user_id: str = Depends(get_current_user)):
    return await delete_course(course_id)


