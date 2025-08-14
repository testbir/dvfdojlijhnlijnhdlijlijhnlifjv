# points_service/main.py

"""
Главная точка входа points_service.
Регистрирует маршруты, CORS, middleware логирования и health-check.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from points_service.api.public import balance as public_balance
from points_service.api.public import transactions as public_transactions
from points_service.api.internal import points as internal_points
from points_service.api import health as health_api
from points_service.utils.monitoring import log_requests

# базовая настройка логирования (можно переопределить через конфиг)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title="Points Service")

# middleware логирования
app.middleware("http")(log_requests)

# CORS (в проде сузить список доменов)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Публичные маршруты
app.include_router(public_balance.router,      prefix="/v1/public",  tags=["Public - Balance"])
app.include_router(public_transactions.router, prefix="/v1/public",  tags=["Public - Transactions"])

# Внутренние маршруты (только для доверенных сервисов)
app.include_router(internal_points.router,     prefix="/v1/internal", tags=["Internal - Points"])

# Health-check без префикса
app.include_router(health_api.router, tags=["Health"])
