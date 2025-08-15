# points_service/schemas/errors.py
from pydantic import BaseModel
from typing import Any, Optional, List, Dict

class ErrorBody(BaseModel):
    code: str
    message: str
    meta: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorBody
