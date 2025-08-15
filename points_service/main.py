# points_service/main.py

"""
Главная точка входа points_service.
Регистрирует маршруты, CORS, middleware логирования и health-check.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from points_service.core.config import settings
from points_service.db.init_db import init_db
from points_service.utils.monitoring import log_requests
from points_service.api import health as health_api
from points_service.api.public import balance as public_balance
from points_service.api.internal import awards as internal_awards

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Points Service")

@app.on_event("startup")
async def _startup():
    await init_db()

app.middleware("http")(log_requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_balance.router, prefix="/v1/public", tags=["Public - Points"])
app.include_router(internal_awards.router, prefix="/v1/internal", tags=["Internal - Points"])
app.include_router(health_api.router, tags=["Health"])
