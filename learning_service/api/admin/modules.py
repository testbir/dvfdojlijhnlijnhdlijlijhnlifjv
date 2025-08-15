# learning_service/api/admin/modules.py


from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from learning_service.db.dependencies import get_db_session
from learning_service.db.tx import commit_or_rollback
from learning_service.models.module import Module
from learning_service.schemas.module import ModuleCreate, ModuleSchema, ModuleUpdate


router_courses = APIRouter(prefix="/courses")
router_modules = APIRouter(prefix="/modules")


@router_courses.post("/{course_id}/modules/", response_model=ModuleSchema, status_code=status.HTTP_201_CREATED)
async def create_module(course_id: int, data: ModuleCreate, response: Response, db: AsyncSession = Depends(get_db_session)):
    order = data.order
    if order is None:
        # транзакционная блокировка по course_id
        await db.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": int(course_id)})
        q = await db.execute(select(func.coalesce(func.max(Module.order), 0)).where(Module.course_id == course_id))
        order = (q.scalar() or 0) + 1

    obj = Module(
        course_id=course_id,
        title=data.title,
        group_title=(data.group_title or None),
        order=order,
        sp_award=data.sp_award or 0,
        completion_message=data.completion_message,
    )
    db.add(obj)
    await commit_or_rollback(db)
    await db.refresh(obj)
    response.headers["Location"] = f"/v1/admin/modules/{obj.id}"
    return obj
@router_modules.get("/{module_id}", response_model=ModuleSchema)
async def get_module(module_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Module).where(Module.id == module_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    return obj

@router_modules.put("/{module_id}", response_model=ModuleSchema)
async def update_module(module_id: int, data: ModuleUpdate, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Module).where(Module.id == module_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await commit_or_rollback(db)
    await db.refresh(obj)
    return obj

@router_modules.delete("/{module_id}", status_code=204)
async def delete_module(module_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Module).where(Module.id == module_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    await db.delete(obj)
    await commit_or_rollback(db)
    return

@router_courses.get("/{course_id}/modules/", response_model=List[ModuleSchema])
async def list_course_modules(course_id: int, db: AsyncSession = Depends(get_db_session)):
    # если в архитектуре курс живет в другом сервисе, можно не 404, но тогда явно это задокументируйте
    res = await db.execute(select(Module).where(Module.course_id == course_id).order_by(Module.order.asc()))
    return res.scalars().all()
