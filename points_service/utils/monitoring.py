# points_service/utils/monitoring.py

"""
Middleware логирования запросов для points_service.
Нужен для записи медленных запросов и ошибок на уровне сервиса.
"""

import time, logging
from fastapi import Request
logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    dur = time.time() - start
    logger.info("%s %s -> %s in %.3fs", request.method, request.url.path, resp.status_code, dur)
    return resp

