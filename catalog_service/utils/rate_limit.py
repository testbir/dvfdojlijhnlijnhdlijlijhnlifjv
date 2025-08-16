#catalog_service/utils/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address
from utils.auth import get_current_user_id
from fastapi.responses import JSONResponse

from core.config import settings

def user_id_or_ip(request):
    try:
        return str(get_current_user_id(request))
    except:
        return get_remote_address(request)

limiter = Limiter(
    key_func=user_id_or_ip,
    default_limits=[settings.GLOBAL_RATE_LIMIT],
    headers_enabled=True,
    storage_uri="memory://",
    strategy="fixed-window"
)

async def custom_rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "⛔ Слишком много запросов. Вы временно заблокированы на 6 минут."},
    )
