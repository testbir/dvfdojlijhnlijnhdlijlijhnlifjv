# admin_service/api/courses.py

from fastapi import APIRouter, Depends, HTTPException
from utils.auth import get_current_admin_user
from services import catalog_api

router = APIRouter(prefix="/admin/courses", tags=["Admin - Courses"])

@router.get("/", dependencies=[Depends(get_current_admin_user)])
async def list_courses():
    return await catalog_api.list_courses()

@router.get("/{course_id}", dependencies=[Depends(get_current_admin_user)])
async def get_course(course_id: int):
    return await catalog_api.get_course(course_id)

@router.post("/", dependencies=[Depends(get_current_admin_user)])
async def create_course(payload: dict):
    return await catalog_api.create_course(payload)

@router.patch("/{course_id}", dependencies=[Depends(get_current_admin_user)])
async def update_course(course_id: int, payload: dict):
    return await catalog_api.update_course(course_id, payload)

@router.delete("/{course_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_course(course_id: int):
    return await catalog_api.delete_course(course_id)
