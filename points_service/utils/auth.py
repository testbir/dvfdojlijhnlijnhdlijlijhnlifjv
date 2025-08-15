# points_service/utils/auth.py

"""
Назначение: авторизация:
 - публичные эндпоинты: извлекаем user_id из JWT.
 - internal/admin эндпоинты: проверяем Bearer INTERNAL_TOKEN.
Используется: в зависимостях роутов.
"""

from fastapi import Request, HTTPException
from jose import jwt, JWTError
from points_service.core.config import settings

def get_current_user_id(request: Request) -> int:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        uid = payload.get("user_id")
        if uid is None:
            raise ValueError
        return int(uid)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="invalid jwt")

class InternalAuth:
    def __call__(self, request: Request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        token = auth.split(" ", 1)[1]
        if token != settings.INTERNAL_TOKEN:
            raise HTTPException(status_code=403, detail="forbidden")
        return True
