# points_service/main.py

"""
Главная точка входа 
Регистрирует маршруты, CORS, middleware логирования и health-check.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from schemas.errors import ErrorResponse, ErrorBody



from core.config import settings
from db.init_db import init_db
from utils.monitoring import log_requests
from api import health as health_api
from api.public import balance as public_balance
from api.internal import awards as internal_awards

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Points Service")

log = logging.getLogger(__name__)

def _json_error(status: int, code: str, message: str, meta=None):
    return JSONResponse(status_code=status, content=ErrorResponse(
        error=ErrorBody(code=code, message=message, meta=meta)
    ).model_dump())

@app.exception_handler(RequestValidationError)
async def _handle_422(request: Request, exc: RequestValidationError):
    return _json_error(422, "validation_error", "Invalid request", exc.errors())

@app.exception_handler(HTTPException)
async def _handle_http_exc(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
    msg = detail.get("message") or detail.get("detail") or str(exc.detail)
    meta = {k: v for k, v in detail.items() if k not in {"message", "detail"}}
    return _json_error(exc.status_code, "http_error", msg, meta or None)

@app.exception_handler(IntegrityError)
async def _handle_integrity(request: Request, exc: IntegrityError):
    log.exception("DB integrity error")
    return _json_error(409, "integrity_error", "Integrity constraint violated")


@app.on_event("startup")
async def _startup():
    await init_db()

app.middleware("http")(log_requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_balance.router, prefix="/v1/public", tags=["Public - Points"])
app.include_router(internal_awards.router, prefix="/v1/internal", tags=["Internal - Points"])
app.include_router(health_api.router, tags=["Health"])
