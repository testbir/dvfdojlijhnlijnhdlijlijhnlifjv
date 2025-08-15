# catalog_service/utils/admin_auth.py

from fastapi import Request, HTTPException, status
import os
ADMIN_TOKEN = os.getenv("INTERNAL_TOKEN", "change-me")

class AdminAuth:
    def __call__(self, request: Request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
        token = auth.split(" ", 1)[1]
        if token != ADMIN_TOKEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return True
