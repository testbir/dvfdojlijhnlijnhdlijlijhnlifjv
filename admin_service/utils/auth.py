# admin_service/utils/auth.py

from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from admin_service.core.config import settings
from admin_service.db import SessionLocal
from admin_service.models.admin import AdminUser  # ожидается таблица админов

def get_current_admin_user(request: Request) -> AdminUser:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        admin_id = payload.get("sub")
        if admin_id is None:
            raise ValueError
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).get(int(admin_id))
        if not admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="admin not found")
        return admin
    finally:
        db.close()
