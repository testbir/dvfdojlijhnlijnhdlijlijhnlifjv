# points_service/utils/auth.py

"""
Назначение: авторизация:
 - публичные эндпоинты: извлекаем user_id из JWT.
 - internal/admin эндпоинты: проверяем Bearer INTERNAL_TOKEN.
Используется: в зависимостях роутов.
"""

from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError

from points_service.core.config import settings


def require_internal_auth(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = auth.split(" ", 1)[1]
    if token != settings.INTERNAL_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return True


def get_current_user_id(request: Request) -> int:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        uid = payload.get("user_id")
        if uid is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return int(uid)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


InternalAuth = Depends(require_internal_auth)
