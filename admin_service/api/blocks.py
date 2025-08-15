# admin_service/api/blocks.py


from fastapi import APIRouter, Depends
from admin_service.utils.auth import get_current_admin_user
from admin_service.services import learning_service as learning_api

router = APIRouter(tags=["Admin - Blocks"])

@router.post("/admin/modules/{module_id}/blocks", dependencies=[Depends(get_current_admin_user)])
async def create_block(module_id: int, payload: dict):
    return await learning_api.create_block(module_id, payload)

@router.patch("/admin/blocks/{block_id}", dependencies=[Depends(get_current_admin_user)])
async def update_block(block_id: int, payload: dict):
    return await learning_api.update_block(block_id, payload)

@router.delete("/admin/blocks/{block_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_block(block_id: int):
    return await learning_api.delete_block(block_id)
