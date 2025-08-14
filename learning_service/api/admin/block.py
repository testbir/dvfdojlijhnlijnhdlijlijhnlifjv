# learning_service/api/admin/block.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from learning_service.db.dependencies import get_db_session
from learning_service.models.block import Block
from learning_service.models.module import Module
from learning_service.schemas.block import BlockCreate, BlockUpdate, BlockSchema

router = APIRouter()

@router.get("/modules/{module_id}/blocks/", response_model=List[BlockSchema])
async def list_blocks(module_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Block).where(Block.module_id == module_id).order_by(Block.order.asc()))
    return res.scalars().all()

@router.post("/modules/{module_id}/blocks/", response_model=BlockSchema)
async def create_block(module_id: int, data: BlockCreate, db: AsyncSession = Depends(get_db_session)):
    # проверим модуль
    m = await db.execute(select(Module).where(Module.id == module_id))
    if not m.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Модуль не найден")

    order = data.order
    if order is None:
        q = await db.execute(select(func.coalesce(func.max(Block.order), 0)).where(Block.module_id == module_id))
        order = (q.scalar() or 0) + 1

    obj = Block(
        module_id=module_id,
        type=data.type,
        title=data.title,
        content=data.content,
        order=order,
        language=data.language,
        video_preview=data.video_preview
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.get("/blocks/{block_id}", response_model=BlockSchema)
async def get_block(block_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Block).where(Block.id == block_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Блок не найден")
    return obj

@router.put("/blocks/{block_id}", response_model=BlockSchema)
async def update_block(block_id: int, data: BlockUpdate, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Block).where(Block.id == block_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Блок не найден")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/blocks/{block_id}")
async def delete_block(block_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Block).where(Block.id == block_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Блок не найден")
    await db.delete(obj)
    await db.commit()
    return {"success": True}
