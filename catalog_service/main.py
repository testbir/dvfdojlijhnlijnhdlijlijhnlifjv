# catalog_service/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
from db.init_db import init_db
from api import (course, progress, module, block, banner, promo, internal, 
                 promocode, accounts, course_modal, student_works, public_course_extras)
from api.learning import course_learning_optimized, module_progress  # 🆕 Новые роутеры
from core.config import settings

from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from utils.rate_limit import limiter, custom_rate_limit_handler
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Course Catalog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

# Основные роутеры
app.include_router(course.router, prefix="/courses", tags=["Courses"])
app.include_router(progress.router, prefix="/progress", tags=["Progress"])
app.include_router(module.router, prefix="/courses", tags=["Modules"])
app.include_router(block.router, prefix="/courses", tags=["Blocks"])
app.include_router(banner.router, tags=["Banners"])
app.include_router(promo.router, prefix="/promos", tags=["Promos"])
app.include_router(internal.router, tags=["Internal"])
app.include_router(promocode.router, tags=["Promocodes"])
app.include_router(accounts.router, prefix="/api", tags=["User Accounts"])
app.include_router(course_modal.router, tags=["Course Modals"])
app.include_router(student_works.router, tags=["Student Works"])
app.include_router(public_course_extras.router, tags=["Public Course Extras"])

# 🆕 Новые роутеры для обучения
app.include_router(course_learning_optimized.router, prefix="/learning/courses", tags=["Learning"])
app.include_router(module_progress.router, prefix="/learning/courses", tags=["Learning - Progress"])