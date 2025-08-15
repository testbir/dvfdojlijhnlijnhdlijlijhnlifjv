# learning_service/utils/admin_auth.py

from fastapi import Request, HTTPException, status

from learning_service.core.config import settings
ADMIN_TOKEN = settings.INTERNAL_TOKEN

class AdminAuth:
    def __call__(self, request: Request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
        if auth.split(" ", 1)[1] != ADMIN_TOKEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return True