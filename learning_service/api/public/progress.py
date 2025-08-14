# learning_service/api/public/progress.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from learning_service.db.dependencies import get_db_session
from learning_service.models.module import Module
from learning_service.models.progress import UserModuleProgress
from learning_service.schemas.progress import CourseProgressResponse, CompleteModuleResponse
from learning_service.utils.auth import get_current_user_id

router = APIRouter(prefix="/progress")

@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
async def get_course_progress(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)

    # все модули отсортированные
    res = await db.execute(select(Module).where(Module.course_id == course_id).order_by(Module.order.asc()))
    modules = res.scalars().all()
    total = len(modules)

    if total == 0:
        return CourseProgressResponse(course_id=course_id, total_modules=0, completed_modules=0, progress_percent=0.0, current_position=None)

    # сколько завершено
    q = await db.execute(
        select(func.count(UserModuleProgress.id))
        .where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id.in_([m.id for m in modules])
        )
    )
    completed = int(q.scalar() or 0)
    percent = round((completed / total) * 100, 2) if total > 0 else 0.0

    # позиция текущего (следующего) модуля = первый незавершенный (1-based)
    completed_ids = set()
    r2 = await db.execute(
        select(UserModuleProgress.module_id)
        .where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id.in_([m.id for m in modules])
        )
    )
    completed_ids = {mid for (mid,) in r2.all()}

    current_pos = None
    for idx, m in enumerate(modules, start=1):
        if m.id not in completed_ids:
            current_pos = idx
            break

    return CourseProgressResponse(
        course_id=course_id,
        total_modules=total,
        completed_modules=completed,
        progress_percent=percent,
        current_position=current_pos
    )

@router.post("/modules/{module_id}/complete", response_model=CompleteModuleResponse)
async def complete_module(module_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)

    # модуль
    res = await db.execute(select(Module).where(Module.id == module_id))
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Модуль не найден")

    # уже завершал?
    dup = await db.execute(
        select(UserModuleProgress).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id == module_id
        )
    )
    existed = dup.scalar_one_or_none()
    if existed:
        return CompleteModuleResponse(
            success=True, awarded_sp=0, already_completed=True, completion_message=None
        )

    # фиксируем прохождение
    db.add(UserModuleProgress(user_id=user_id, module_id=module_id))
    await db.commit()

    # TODO: при интеграции с points_service — отправить событие начисления m.sp_award
    return CompleteModuleResponse(
        success=True,
        awarded_sp=int(m.sp_award or 0),
        already_completed=False,
        completion_message=m.completion_message
    )
