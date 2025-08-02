# admin_service/api/blocks.py


import httpx
from fastapi import APIRouter, HTTPException
from schemas import ContentBlockCreate, BlockOrderUpdateSchema
from typing import List
from core.config import settings
from utils.auth import get_current_user
from fastapi import Depends
from utils.auth import get_current_admin_user
from models.admin import AdminUser
from services.catalog_api import (get_block, 
                                  update_block, 
                                  delete_block, 
                                  get_blocks_for_module,
                                  update_blocks_order)

router = APIRouter()
CATALOG_URL = settings.CATALOG_SERVICE_URL


@router.post("/admin/modules/{module_id}/blocks/", summary="Создат контент-блок для модуля")
async def create_block(module_id: int, data: ContentBlockCreate, current_admin: AdminUser = Depends(get_current_admin_user)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{CATALOG_URL}/courses/internal/modules/{module_id}/blocks/",
                json=data.dict()
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        return response.json()



@router.get("/admin/blocks/{block_id}", summary="Получить контент-блок по ID")
async def retrieve_block(block_id: int, current_admin: AdminUser = Depends(get_current_admin_user)):
    return await get_block(block_id)

@router.put("/admin/blocks/{block_id}", summary="Обновить контент-блок по ID")
async def edit_block(block_id: int, data: ContentBlockCreate, current_admin: AdminUser = Depends(get_current_admin_user)):
    return await update_block(block_id, data)

@router.delete("/admin/blocks/{block_id}", summary="Удалить контент-блок по ID")
async def remove_block(block_id: int, current_admin: AdminUser = Depends(get_current_admin_user)):
    return await delete_block(block_id)

@router.get("/admin/modules/{module_id}/blocks/", summary="Получить список блоков для модуля")
async def list_blocks_for_module(module_id: int, current_admin: AdminUser = Depends(get_current_admin_user)):
    return await get_blocks_for_module(module_id)


@router.put("/admin/modules/{module_id}/blocks/order/", summary="Обновить порядок блоков в модуле")
async def update_block_order(
    module_id: int, 
    blocks: List[BlockOrderUpdateSchema], 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    data = [block.dict() for block in blocks]
    return await update_blocks_order(module_id, data)

