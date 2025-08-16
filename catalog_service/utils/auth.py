# catalog_service/utils/auth.py

from jose import JWTError, jwt
from fastapi import Request, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import Optional

from core.config import settings

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"


def get_current_user_id(request: Request) -> Optional[int]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Нет токена")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")  # Django кладёт user_id
    except JWTError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
