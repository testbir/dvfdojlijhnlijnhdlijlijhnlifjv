# learning_service/api/admin/modules.py


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from learning_service.db.dependencies import get_db_session
from learning_service.models.module import Module
from learning_service.schemas.module import ModuleCreate, ModuleUpdate, ModuleSchema

router_courses = APIRouter(prefix="/courses")
router_modules = APIRouter(prefix="/modules")


@router_courses.post("/{course_id}/modules/", response_model=ModuleSchema)
async def create_module(course_id: int, data: ModuleCreate, db: AsyncSession = Depends(get_db_session)):
    # авто-order если не задан: max(order)+1 в рамках курса
    order = data.order
    if order is None:
        q = await db.execute(select(func.coalesce(func.max(Module.order), 0)).where(Module.course_id == course_id))
        order = (q.scalar() or 0) + 1

    obj = Module(
        course_id=course_id,
        title=data.title,
        group_title=(data.group_title or None),
        order=order,
        sp_award=data.sp_award or 0,
        completion_message=data.completion_message
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
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

    await db.commit()
    await db.refresh(obj)
    return obj

@router_modules.delete("/{module_id}")
async def delete_module(module_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Module).where(Module.id == module_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    await db.delete(obj)
    await db.commit()
    return {"success": True}

@router_courses.get("/{course_id}/modules/", response_model=List[ModuleSchema])
async def list_course_modules(course_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Module).where(Module.course_id == course_id).order_by(Module.order.asc()))
    return res.scalars().all()
