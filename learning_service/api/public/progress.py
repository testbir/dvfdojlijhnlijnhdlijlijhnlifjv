# learning_service/api/public/progress.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.internal.points import award_points
from db.dependencies import get_db_session
from models.module import Module
from models.progress import UserModuleProgress
from schemas.progress import CompleteModuleResponse, CourseProgressResponse
from utils.auth import get_current_user_id
from core.config import settings
import httpx

router = APIRouter(prefix="/progress")


@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
async def get_course_progress(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)
    res = await db.execute(select(Module).where(Module.course_id == course_id).order_by(Module.order.asc(), Module.id.asc()))
    modules = res.scalars().all()
    total = len(modules)
    if total == 0:
        return CourseProgressResponse(course_id=course_id, total_modules=0, completed_modules=0, progress_percent=0.0, current_position=None)

    q = await db.execute(
        select(func.count(UserModuleProgress.id))
        .where(UserModuleProgress.user_id == user_id, UserModuleProgress.module_id.in_([m.id for m in modules]))
    )
    completed = int(q.scalar() or 0)
    percent = round((completed / total) * 100, 2) if total > 0 else 0.0

    done_ids_res = await db.execute(select(UserModuleProgress.module_id).where(UserModuleProgress.user_id == user_id))
    done_ids = set(i for (i,) in done_ids_res.all())
    current_pos = None
    for idx, m in enumerate(modules, start=1):
        if m.id not in done_ids:
            current_pos = idx
            break

    return CourseProgressResponse(
        course_id=course_id,
        total_modules=total,
        completed_modules=completed,
        progress_percent=percent,
        current_position=current_pos,
    )


@router.post("/modules/{module_id}/complete/", response_model=CompleteModuleResponse)
async def complete_module(module_id: int, db: AsyncSession = Depends(get_db_session), user_id: int = Depends(get_current_user_id)):
    m = (await db.execute(select(Module).where(Module.id == module_id))).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Модуль не найден")

    # пробуем создать прогресс
    prog = UserModuleProgress(user_id=user_id, module_id=module_id)
    db.add(prog)
    try:
        await db.commit()
        already = False
    except Exception:
        await db.rollback()
        # возможно уже завершён
        exists = await db.execute(select(UserModuleProgress.id).where(
            UserModuleProgress.user_id == user_id, UserModuleProgress.module_id == module_id))
        if not exists.scalar_one_or_none():
            raise
        already = True

    awarded = 0
    if not already and m.sp_award > 0:
        try:
            await award_points(user_id, m.sp_award, f"complete_module:{module_id}", f"{user_id}:{module_id}")
            awarded = m.sp_award
        except Exception:
            # логируем, но не падаем
            pass

    return CompleteModuleResponse(success=True, awarded_sp=awarded, already_completed=already, completion_message=m.completion_message)