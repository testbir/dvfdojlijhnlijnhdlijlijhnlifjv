# admin_service/api/modules.py

from fastapi import APIRouter, Depends
from admin_service.utils.auth import get_current_admin_user
from admin_service.services import learning_api

router = APIRouter(tags=["Admin - Modules"])

@router.post("/admin/courses/{course_id}/modules", dependencies=[Depends(get_current_admin_user)])
async def create_module(course_id: int, payload: dict):
    return await learning_api.create_module(course_id, payload)

@router.patch("/admin/modules/{module_id}", dependencies=[Depends(get_current_admin_user)])
async def update_module(module_id: int, payload: dict):
    return await learning_api.update_module(module_id, payload)

@router.delete("/admin/modules/{module_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_module(module_id: int):
    return await learning_api.delete_module(module_id)
