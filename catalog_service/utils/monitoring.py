# catalog_service/utils/monitoring.py


import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Логируем медленные запросы
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    # Логируем ошибки
    if response.status_code >= 400:
        logger.error(
            f"Error: {request.method} {request.url.path} "
            f"returned {response.status_code}"
        )
    
    return response