# admin_service/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from admin_service.db import Base, engine
from admin_service.api import health as health_api
from admin_service.api import auth as auth_api
from admin_service.api import courses as courses_api
from admin_service.api import modules as modules_api
from admin_service.api import blocks as blocks_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Admin Service")

@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(health_api.router)
app.include_router(auth_api.router)
app.include_router(courses_api.router)
app.include_router(modules_api.router)
app.include_router(blocks_api.router)
