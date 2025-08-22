# id_service/main.py
"""
Главный модуль FastAPI.

Добавлено:
- Глобальные JSON-хендлеры ошибок:
  * HTTPException → {"error":{"code", "message", "details?"}}
  * RequestValidationError → {"error":{"code":422, "message":"Validation error", "details":[...]}}
- JSONContentTypeMiddleware: для небезопасных методов под /auth/** и /account/** требуем Content-Type: application/json
  (исключение: /auth/csrf).
- AuthCacheHeadersMiddleware: на /auth/** и /oidc/** выставляем Cache-Control: no-store и Pragma: no-cache
  (исключения: discovery и jwks).
Порядок middleware: SecurityHeaders → JSONContentType → CSRF → AuthCacheHeaders → CORS → TrustedHost(prod).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from utils.csrf import csrf_protection
from core.config import settings
from db.init_db import init_db
from db.session import async_session_maker, engine
from db.base import Base
from services.jwk_service import jwk_service
from services.backchannel_logout import backchannel_logout_service
from utils import rate_limiter, setup_logging

# Routers
from api.oidc import discovery, authorize, token, userinfo, logout, jwks, revoke
from api.auth import register, login, password_reset, email_verification
from api.auth import csrf as csrf_api
from api.account import profile, email_change, password_change, delete_account
from api import health

from pydantic import ValidationError

# Logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация приложения на старте."""
    logger.info("Starting ID Service...")

    # Инициализация БД/сервисов
    async with async_session_maker() as session:
        await init_db(session)
    await jwk_service.ensure_active_key()
    await rate_limiter.init()

    yield

    # Cleanup
    logger.info("Shutting down ID Service...")
    await backchannel_logout_service.cleanup()
    await rate_limiter.close()
    await engine.dispose()


app = FastAPI(
    title="ID Service",
    description="OpenID Connect Identity Provider for asynq.ru",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if settings.APP_ENV == "development" else None,
    lifespan=lifespan,
)

# ---------------------------
# Global middlewares
# ---------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Базовые security-заголовки на все ответы."""
    async def dispatch(self, request, call_next):
        resp = await call_next(request)
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        if settings.APP_ENV == "production":
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
        return resp


class JSONContentTypeMiddleware(BaseHTTPMiddleware):
    """Для /auth/** и /account/** требуем JSON на небезопасных методах."""
    def _needs_json(self, path: str) -> bool:
        if path == "/auth/csrf":
            return False
        return path.startswith("/auth/") or path.startswith("/account/")

    async def dispatch(self, request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and self._needs_json(request.url.path):
            ct = request.headers.get("content-type", "")
            if "application/json" not in ct.lower():
                # 415 Unsupported Media Type — явный сигнал клиенту
                return JSONResponse(
                    {"error": {"code": 415, "message": "Content-Type must be application/json", "details": {"required": "application/json"}}},
                    status_code=415,
                )
        return await call_next(request)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Проверка CSRF по заголовку X-CSRF-Token (double-submit cookie)."""
    async def dispatch(self, request, call_next):
        if csrf_protection.should_check_csrf(request):
            await csrf_protection.validate_token(request)
        return await call_next(request)


class AuthCacheHeadersMiddleware(BaseHTTPMiddleware):
    """Отключаем кэш для /auth/** и OIDC-эндпоинтов.
    Исключения: discovery и jwks.
    """
    DISCOVERY = "/.well-known/openid-configuration"
    JWKS = "/.well-known/jwks.json"
    OIDC_PATHS = {
        "/authorize",
        "/token",
        "/revoke",
        "/userinfo",
        "/logout",
    }

    async def dispatch(self, request: Request, call_next):
        resp = await call_next(request)
        path = request.url.path

        is_auth = path.startswith("/auth/")
        # учитываем как корневые OIDC пути, так и гипотетический префикс /oidc/
        is_oidc = path in self.OIDC_PATHS or path.startswith("/oidc/")
        is_static = path in {self.DISCOVERY, self.JWKS}

        if (is_auth or is_oidc) and not is_static:
            resp.headers.setdefault("Cache-Control", "no-store")
            resp.headers.setdefault("Pragma", "no-cache")
        return resp



# Порядок имеет значение
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(JSONContentTypeMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(AuthCacheHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if settings.APP_ENV == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["id.asynq.ru", "*.asynq.ru"])


# ---------------------------
# Routers
# ---------------------------

# OIDC endpoints
app.include_router(discovery.router, tags=["OIDC Discovery"])
app.include_router(jwks.router, tags=["OIDC JWKS"])
app.include_router(authorize.router, tags=["OIDC Authorization"])
app.include_router(token.router, tags=["OIDC Token"])
app.include_router(userinfo.router, tags=["OIDC UserInfo"])
app.include_router(logout.router, tags=["OIDC Logout"])
app.include_router(revoke.router, tags=["OIDC Token"])

# Auth endpoints
app.include_router(register.router, prefix="/auth", tags=["Authentication"])
app.include_router(login.router, prefix="/auth", tags=["Authentication"])
app.include_router(password_reset.router, prefix="/auth", tags=["Authentication"])
app.include_router(email_verification.router, prefix="/auth", tags=["Authentication"])
app.include_router(csrf_api.router, prefix="/auth", tags=["Authentication"])

# Account management endpoints
app.include_router(profile.router, prefix="/account", tags=["Account"])
app.include_router(email_change.router, prefix="/account", tags=["Account"])
app.include_router(password_change.router, prefix="/account", tags=["Account"])
app.include_router(delete_account.router, prefix="/account", tags=["Account"])

# Health
app.include_router(health.router, tags=["Health"])


@app.get("/")
async def root():
    return {"service": "ID Service", "version": "1.0.0", "issuer": settings.ISSUER}


# ---------------------------
# Global exception handlers
# ---------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Унифицированные JSON-ошибки для всех не-OAuth ручек.
    /oidc/token и /oidc/revoke сами формируют RFC-ошибки и сюда не попадут,
    т.к. возвращают JSONResponse напрямую.
    """
    payload = {"error": {"code": exc.status_code, "message": exc.detail}}
    return JSONResponse(payload, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Валидационные ошибки Pydantic/FastAPI → единый формат."""
    details = exc.errors()
    payload = {"error": {"code": 422, "message": "Validation error", "details": details}}
    return JSONResponse(payload, status_code=422)

@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        {"error": {"code": 422, "message": "Validation error", "details": exc.errors()}},
        status_code=422,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development",
        log_level="debug" if settings.APP_ENV == "development" else "info",
    )
