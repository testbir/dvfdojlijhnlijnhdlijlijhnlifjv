# learning_service/core/errors.py

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

CONSTRAINT_MAP = {
    "uq_course_module_title": ("MODULE_TITLE_TAKEN", "Модуль с таким названием уже существует в курсе"),
    "uq_course_module_order": ("MODULE_ORDER_TAKEN", "Порядковый номер модуля уже занят в этом курсе"),
    "uq_block_order_in_module": ("BLOCK_ORDER_TAKEN", "Порядковый номер блока уже занят в этом модуле"),
}

def problem(code: str, message: str, details: dict | None = None, status_code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message, "details": details or {}}})

def setup_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def on_validation_error(_: Request, exc: RequestValidationError):
        # 422 -> 400 с нормализованными полями
        return problem("VALIDATION_ERROR", "Неверные входные данные", {"errors": exc.errors()}, status.HTTP_400_BAD_REQUEST)

    @app.exception_handler(ValidationError)
    async def on_pydantic_validation(_: Request, exc: ValidationError):
        return problem("VALIDATION_ERROR", "Неверные входные данные", {"errors": exc.errors()}, status.HTTP_400_BAD_REQUEST)

    @app.exception_handler(IntegrityError)
    async def on_integrity(_: Request, exc: IntegrityError):
        name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None) or ""
        code, msg = CONSTRAINT_MAP.get(name, ("INTEGRITY_ERROR", "Нарушение ограничений БД"))
        return problem(code, msg, {"constraint": name}, status.HTTP_409_CONFLICT)


