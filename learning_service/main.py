# learning_service/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from core.errors import setup_error_handlers

from api.admin import modules as admin_modules, blocks as admin_blocks
from api.public import courses as public_courses, progress as public_progress
from api import health as health_api
from utils.admin_auth import AdminAuth

# ⬇️ добавьте
import os
from core.base import Base
from db.init_db import engine

app = FastAPI(title="Learning Service")

@app.on_event("startup")
async def _startup():
    setup_error_handlers(app)
    # ⬇️ fallback: если нет миграций — создаём таблицы
    if not os.path.exists("alembic.ini"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

deps = [Depends(AdminAuth())]
app.include_router(admin_modules.router_courses, prefix="/v1/admin", tags=["Admin - Modules"], dependencies=deps)
app.include_router(admin_modules.router_modules, prefix="/v1/admin", tags=["Admin - Modules"], dependencies=deps)
app.include_router(admin_blocks.router_modules,  prefix="/v1/admin", tags=["Admin - Blocks"],  dependencies=deps)
app.include_router(admin_blocks.router_blocks,   prefix="/v1/admin", tags=["Admin - Blocks"],  dependencies=deps)

app.include_router(public_courses.router,  prefix="/v1/public", tags=["Public - Courses/Modules"])
app.include_router(public_progress.router, prefix="/v1/public", tags=["Public - Progress"])
app.include_router(health_api.router, tags=["Health"])
