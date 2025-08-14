# points_service/utils/monitoring.py

"""
Middleware логирования запросов для points_service.
Нужен для записи медленных запросов и ошибок на уровне сервиса.
"""

import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

SLOW_REQUEST_THRESHOLD_SEC = 1.0

async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    if duration > SLOW_REQUEST_THRESHOLD_SEC:
        logger.warning(
            "Slow request: %s %s took %.2fs",
            request.method, request.url.path, duration
        )

    if response.status_code >= 400:
        logger.error(
            "Error response: %s %s -> %s",
            request.method, request.url.path, response.status_code
        )

    return response
