# learning_service/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from learning_service.db.init_db import init_db

from learning_service.api.admin import modules as admin_modules, blocks as admin_blocks
from learning_service.api.public import courses as public_courses, progress as public_progress
from learning_service.api import health as health_api
from learning_service.utils.admin_auth import AdminAuth

app = FastAPI(title="Learning Service")

@app.on_event("startup")
async def _startup():
    await init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

# admin (защита INTERNAL_TOKEN)
deps = [Depends(AdminAuth())]
app.include_router(admin_modules.router_courses, prefix="/v1/admin", tags=["Admin - Modules"], dependencies=deps)
app.include_router(admin_modules.router_modules, prefix="/v1/admin", tags=["Admin - Modules"], dependencies=deps)
app.include_router(admin_blocks.router_modules,  prefix="/v1/admin", tags=["Admin - Blocks"],  dependencies=deps)
app.include_router(admin_blocks.router_blocks,   prefix="/v1/admin", tags=["Admin - Blocks"],  dependencies=deps)

# public
app.include_router(public_courses.router,  prefix="/v1/public", tags=["Public - Courses/Modules"])
app.include_router(public_progress.router, prefix="/v1/public", tags=["Public - Progress"])
app.include_router(health_api.router, tags=["Health"])
