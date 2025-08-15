# learning_service/utils/auth.py

from fastapi import Request, HTTPException
from jose import jwt, JWTError
from learning_service.core.config import settings

def get_current_user_id(request: Request) -> int:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        uid = payload.get("user_id")
        if uid is None:
            raise ValueError
        return int(uid)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="invalid jwt")
