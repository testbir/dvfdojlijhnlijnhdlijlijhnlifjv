# admin_service/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import Base, engine

from api import health as health_api
from api import auth as auth_api
from api import courses as courses_api
from api import modules as modules_api
from api import blocks as blocks_api
from api import homepage as homepage_api
from api import course_extras as course_extras_api
from api import statistics as statistics_api
from api import users as users_api
from api import bulk_operations as bulk_operations_api
from api import upload as upload_api
from api import promocodes as admin_promocodes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Admin Service", version="2.0.0")

@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=engine)
    logging.info("Database initialized")

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
app.include_router(homepage_api.router)
app.include_router(course_extras_api.router)
app.include_router(statistics_api.router)
app.include_router(users_api.router)
app.include_router(bulk_operations_api.router)
app.include_router(upload_api.router)
app.include_router(admin_promocodes.router)

@app.get("/")
async def root():
    return {"message": "Admin Service v2.0.0", "status": "running"}
