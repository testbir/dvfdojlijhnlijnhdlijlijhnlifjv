# catalog_service/api/block.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.dependencies import get_db_session
from models.content import ContentBlock
from schemas.block import ContentBlockCreateSchema, BlockOrderUpdate, ContentBlockSchema, SUPPORTED_LANGUAGES

router = APIRouter()

@router.put("/internal/blocks/{block_id}", summary="Обновление контент-блока (admin)")
async def admin_update_block(block_id: int, data: ContentBlockCreateSchema, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(ContentBlock).where(ContentBlock.id == block_id))
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Контент-блок не найден")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(block, key, value)

    await db.commit()
    await db.refresh(block)
    return {"id": block.id, "message": "Контент-блок обновлён"}

@router.delete("/internal/blocks/{block_id}", summary="Удаление контент-блока (admin)")
async def admin_delete_block(block_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(ContentBlock).where(ContentBlock.id == block_id))
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Контент-блок не найден")

    await db.delete(block)
    await db.commit()
    return {"message": "Контент-блок удалён"}

@router.get("/internal/blocks/{block_id}", summary="Получение данных контент-блока (admin)")
async def admin_get_block(block_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(ContentBlock).where(ContentBlock.id == block_id))
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Контент-блок не найден")
    
    return {
        "id": block.id,
        "type": block.type,
        "title": block.title,
        "order": block.order,
        "content": block.content,
        "video_preview": block.video_preview,
        "language": block.language  # Добавляем язык
    }

@router.get("/internal/languages", summary="Получить список поддерживаемых языков программирования")
async def get_supported_languages():
    """Возвращает список поддерживаемых языков для блоков кода"""
    return SUPPORTED_LANGUAGES