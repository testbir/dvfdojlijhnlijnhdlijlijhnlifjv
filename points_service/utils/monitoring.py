# points_service/utils/monitoring.py

"""
Middleware логирования запросов для points_service.
Нужен для записи медленных запросов и ошибок на уровне сервиса.
"""

import uuid, time, logging
from fastapi import Request
logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start = time.time()
    try:
        resp = await call_next(request)
    except Exception:
        logger.exception("ERR %s %s rid=%s", request.method, request.url.path, rid)
        raise
    dur = time.time() - start
    resp.headers["X-Request-ID"] = rid
    logger.info("%s %s -> %s in %.3fs rid=%s", request.method, request.url.path, resp.status_code, dur, rid)
    return resp
