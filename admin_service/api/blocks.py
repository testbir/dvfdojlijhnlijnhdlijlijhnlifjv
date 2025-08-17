# admin_service/api/blocks.py


from fastapi import APIRouter, Depends
from utils.auth import get_current_admin_user
from services import learning_service as learning_api

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


@router.post("/admin/blocks/reorder/", dependencies=[Depends(get_current_admin_user)])
async def reorder_blocks(payload: dict):
    """Изменить порядок блоков"""
    module_id = payload.get("module_id")
    blocks_order = payload.get("blocks_order", [])
    
    # Прокси запрос к learning_service
    return await learning_api.reorder_blocks(module_id, blocks_order)