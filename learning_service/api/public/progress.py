# learning_service/api/public/progress.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import httpx

from learning_service.db.dependencies import get_db_session
from learning_service.models.module import Module
from learning_service.models.progress import UserModuleProgress
from learning_service.schemas.progress import CourseProgressResponse, CompleteModuleResponse
from learning_service.utils.auth import get_current_user_id
from learning_service.core.config import settings

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

@router.post("/complete/{module_id}", response_model=CompleteModuleResponse)
async def complete_module(module_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)

    res = await db.execute(select(Module).where(Module.id == module_id))
    module = res.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="module not found")

    inserted = False
    try:
        async with db.begin():
            await db.execute(UserModuleProgress.__table__.insert().values(user_id=user_id, module_id=module_id))
        inserted = True
    except Exception:
        inserted = False  # already completed

    awarded = 0
    if inserted and int(getattr(module, "sp_award", 0)) > 0:
        idem = f"module_complete:{user_id}:{module_id}"
        try:
            async with httpx.AsyncClient(base_url=settings.POINTS_SERVICE_URL, timeout=5.0) as client:
                await client.post(
                    "/v1/internal/points/award",
                    headers={"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"},
                    json={
                        "user_id": user_id,
                        "amount": int(module.sp_award),
                        "reason": "module_complete",
                        "idempotency_key": idem,
                        "source_service": "learning_service",
                        "reference_type": "module",
                        "reference_id": str(module_id),
                    },
                )
            awarded = int(module.sp_award)
        except Exception:
            awarded = 0

    return CompleteModuleResponse(
        success=True,
        awarded_sp=awarded,
        already_completed=not inserted,
        completion_message=getattr(module, "completion_message", None),
    )
