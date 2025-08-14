# learning_service/api/public/courses.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict

from learning_service.db.dependencies import get_db_session
from learning_service.models.module import Module
from learning_service.models.block import Block
from learning_service.models.progress import UserModuleProgress
from learning_service.schemas.module import ModuleSchema

from learning_service.utils.auth import get_current_user_id

router = APIRouter(prefix="/courses")

@router.get("/{course_id}/groups")
async def get_course_outline_grouped(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    # группированная структура: группы -> модули
    res = await db.execute(select(Module).where(Module.course_id == course_id).order_by(Module.order.asc()))
    modules = res.scalars().all()
    if not modules:
        # не ошибка — просто пустая структура
        return {"course_id": course_id, "groups": []}

    # отметим завершённые модули пользователя (если авторизован)
    completed_ids: set[int] = set()
    try:
        user_id = get_current_user_id(request)
        q = await db.execute(select(UserModuleProgress.module_id).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id.in_([m.id for m in modules])
        ))
        completed_ids = {mid for (mid,) in q.all()}
    except:
        pass

    groups: Dict[Optional[str], List[dict]] = {}
    for m in modules:
        g = m.group_title
        groups.setdefault(g, [])
        groups[g].append({
            "id": m.id,
            "course_id": m.course_id,
            "title": m.title,
            "order": m.order,
            "sp_award": m.sp_award,
            "completed": m.id in completed_ids
        })

    # порядок групп — по минимальному order внутри группы
    def group_sort_key(items: List[dict]) -> int:
        return min(x["order"] for x in items) if items else 10**9

    grouped = [
        {"group_title": g, "modules": sorted(items, key=lambda x: x["order"])}
        for g, items in sorted(groups.items(), key=lambda kv: group_sort_key(kv[1]))
    ]
    return {"course_id": course_id, "groups": grouped}

@router.get("/modules/{module_id}", response_model=ModuleSchema)
async def get_module_detail(module_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Module).where(Module.id == module_id))
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    return m

@router.get("/modules/{module_id}/blocks")
async def get_module_blocks(module_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Block).where(Block.module_id == module_id).order_by(Block.order.asc()))
    blocks = res.scalars().all()
    return [
        {
            "id": b.id,
            "type": b.type,
            "title": b.title,
            "content": b.content,
            "order": b.order,
            "language": b.language,
            "video_preview": b.video_preview,
        } for b in blocks
    ]
