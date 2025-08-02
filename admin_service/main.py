# admin_service/main.py

from fastapi import FastAPI, Request
from api import (courses, modules, blocks, auth, homepage, upload, 
                 users, statistics, bulk_operations, promocodes, course_extras)  # Добавляем course_extras
from db import Base, engine
from models import admin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Admin Panel")

@app.middleware("http")
async def debug_path_logger(request: Request, call_next):
    print("📥 PATH:", request.url.path)
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("🔧 Создание таблиц...")
    Base.metadata.create_all(bind=engine)

# Включаем роутеры
app.include_router(upload.router)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(modules.router)
app.include_router(blocks.router)
app.include_router(homepage.router)
app.include_router(users.router)          
app.include_router(statistics.router)      
app.include_router(bulk_operations.router) 
app.include_router(promocodes.router)
app.include_router(course_extras.router)  # Добавляем новый роутер