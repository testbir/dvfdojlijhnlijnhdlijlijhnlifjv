# learning_service/api/public/courses.py

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learning_service.db.dependencies import get_db_session
from learning_service.models.block import Block
from learning_service.models.module import Module
from learning_service.models.progress import UserModuleProgress
from learning_service.schemas.block import BlockSchema
from learning_service.schemas.module import ModuleSchema
from learning_service.utils.auth import get_current_user_id


router = APIRouter(prefix="/courses")

@router.get("/{course_id}/groups")
async def get_course_outline_grouped(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Module).where(Module.course_id == course_id).order_by(Module.order.asc(), Module.id.asc()))
    modules = res.scalars().all()

    completed_ids: set[int] = set()
    try:
        user_id = get_current_user_id(request)
        q = await db.execute(select(UserModuleProgress.module_id).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id.in_([m.id for m in modules])
        ))
        completed_ids = {mid for (mid,) in q.all()}
    except Exception:
        completed_ids = set()

    groups: Dict[Optional[str], List[dict]] = {}
    for m in modules:
        g = m.group_title
        groups.setdefault(g, []).append({
            "id": m.id,
            "title": m.title,
            "order": m.order,
            "sp_award": int(getattr(m, "sp_award", 0) or 0),
            "completed": m.id in completed_ids,
        })
    result = []
    for g, items in groups.items():
        result.append({"group_title": g, "modules": items})
    return {"course_id": course_id, "groups": result}

@router.get("/modules/{module_id}", response_model=ModuleSchema)
async def get_module(module_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Module).where(Module.id == module_id))
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="module not found")
    return ModuleSchema.model_validate(m, from_attributes=True)

@router.get("/modules/{module_id}/blocks", response_model=List[BlockSchema])
async def get_module_blocks(module_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Block).where(Block.module_id == module_id).order_by(Block.order.asc(), Block.id.asc()))
    blocks = res.scalars().all()
    return [BlockSchema.model_validate(b, from_attributes=True) for b in blocks]
