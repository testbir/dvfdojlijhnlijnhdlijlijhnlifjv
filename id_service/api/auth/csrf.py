# id_service/api/auth/csrf.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from core.config import settings
from utils.csrf import csrf_protection

router = APIRouter()

@router.get("/csrf")
async def get_csrf():
    token = csrf_protection.generate_token()
    resp = JSONResponse({"csrf_token": token})
    resp.set_cookie(
        key=csrf_protection.cookie_name,
        value=token,
        path="/",
        httponly=False,  # double-submit
        secure=(settings.APP_ENV == "production"),
        samesite="lax",
    )
    return resp