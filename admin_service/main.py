# admin_service/main.py

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Блок БД (как просили) ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:siperup44rQVr8@db:5432/team_platform_admin",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Импорты моделей и схем (как просили) ---
# При необходимости скорректируйте пути импорта под вашу структуру
try:
    from models import Admin, Course, Module, ModuleGroup, ContentBlock  # type: ignore
except Exception:
    pass

try:
    from schemas import (
        CourseCreate,
        ModuleCreate,
        ContentBlockCreate,
        AdminLogin,
        TokenResponse,
        BlockOrderUpdateSchema,
        BannerCreate,
        PromoCreate,
    )  # type: ignore
except Exception:
    pass

# --- Остальной код из вашего текущего main.py без изменений ---

from api import health as health_api
from api import auth as auth_api
from api import courses as courses_api
from api import modules as modules_api
from api import blocks as blocks_api
from api import homepage as homepage_api
from api import banners as banners_api
from api import course_extras as course_extras_api
from api import statistics as statistics_api
from api import users as users_api
from api import bulk_operations as bulk_operations_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Admin Service", version="2.0.0")


@app.on_event("startup")
def _startup():
    # Инициализация БД при старте
    Base.metadata.create_all(bind=engine)
    logging.info("Database initialized")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(health_api.router)
app.include_router(auth_api.router)
app.include_router(courses_api.router)
app.include_router(modules_api.router)
app.include_router(blocks_api.router)
app.include_router(homepage_api.router)
app.include_router(banners_api.router)
app.include_router(course_extras_api.router)
app.include_router(statistics_api.router)
app.include_router(users_api.router)
app.include_router(bulk_operations_api.router)


# Базовый эндпоинт для проверки
@app.get("/")
async def root():
    return {"message": "Admin Service v2.0.0", "status": "running"}
