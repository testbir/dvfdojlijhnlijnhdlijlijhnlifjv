# learning_service/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from learning_service.api.admin import modules as admin_modules, blocks as admin_blocks
from learning_service.api.public import courses as public_courses, progress as public_progress

app = FastAPI(title="Learning Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

# admin
app.include_router(admin_modules.router_courses, prefix="/v1/admin", tags=["Admin - Modules"])
app.include_router(admin_modules.router_modules, prefix="/v1/admin", tags=["Admin - Modules"])
app.include_router(admin_blocks.router_modules,  prefix="/v1/admin", tags=["Admin - Blocks"])
app.include_router(admin_blocks.router_blocks,   prefix="/v1/admin", tags=["Admin - Blocks"])
# public
app.include_router(public_courses.router,  prefix="/v1/public", tags=["Public - Courses/Modules"])
app.include_router(public_progress.router, prefix="/v1/public", tags=["Public - Progress"])
