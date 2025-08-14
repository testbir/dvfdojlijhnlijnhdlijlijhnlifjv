# points_service/schemas/points.py

"""
Назначение: pydantic-схемы запросов/ответов для API.
Используется: во всех эндпоинтах.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime


class BalanceResponse(BaseModel):
    balance: int


class TransactionSchema(BaseModel):
    id: int
    user_id: int
    delta: int
    type: Literal["award", "spend", "refund", "adjust"]
    reason: Optional[str] = None
    source_service: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    idempotency_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionsListResponse(BaseModel):
    items: List[TransactionSchema]
    total: int
    limit: int
    offset: int


class InternalAwardRequest(BaseModel):
    user_id: int
    amount: int = Field(..., gt=0)
    reason: Optional[str] = "module_complete"
    idempotency_key: str = Field(..., min_length=8, max_length=255)
    source_service: str = Field(default="learning_service", max_length=64)
    reference_type: Optional[str] = Field(default="module", max_length=64)
    reference_id: Optional[str] = Field(default=None, max_length=128)


class InternalSpendRequest(BaseModel):
    user_id: int
    amount: int = Field(..., gt=0)
    reason: Optional[str] = "spend"
    idempotency_key: str = Field(..., min_length=8, max_length=255)
    source_service: str = Field(default="unknown", max_length=64)
    reference_type: Optional[str] = Field(default=None, max_length=64)
    reference_id: Optional[str] = Field(default=None, max_length=128)


class InternalRefundRequest(BaseModel):
    user_id: int
    amount: int = Field(..., gt=0)
    reason: Optional[str] = "refund"
    idempotency_key: str = Field(..., min_length=8, max_length=255)
    source_service: str = Field(default="unknown", max_length=64)
    reference_type: Optional[str] = Field(default=None, max_length=64)
    reference_id: Optional[str] = Field(default=None, max_length=128)


class InternalMutationResponse(BaseModel):
    success: bool
    balance: int
    transaction: TransactionSchema


class AdminAdjustRequest(BaseModel):
    user_id: int
    delta: int = Field(..., ne=0)
    reason: Optional[str] = "admin_adjust"
    idempotency_key: str = Field(..., min_length=8, max_length=255)
