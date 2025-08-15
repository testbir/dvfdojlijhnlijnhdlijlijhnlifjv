# admin_service/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from admin_service.db import Base, engine
from admin_service.api import health as health_api
from admin_service.api import auth as auth_api
from admin_service.api import courses as courses_api
from admin_service.api import modules as modules_api
from admin_service.api import blocks as blocks_api
from admin_service.api import homepage as homepage_api
from admin_service.api import banners as banners_api
from admin_service.api import course_extras as course_extras_api
from admin_service.api import statistics as statistics_api
from admin_service.api import users as users_api
from admin_service.api import bulk_operations as bulk_operations_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Admin Service", version="2.0.0")

@app.on_event("startup")
def _startup():
    """Инициализация БД при старте"""
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

# Добавляем базовый эндпоинт для проверки
@app.get("/")
async def root():
    return {"message": "Admin Service v2.0.0", "status": "running"}