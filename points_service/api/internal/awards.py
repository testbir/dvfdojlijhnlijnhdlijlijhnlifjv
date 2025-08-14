# points_service/api/internal/awards.py

"""
Назначение: внутренние эндпоинты для начисления/списания/рефанда SP.
Требует INTERNAL_TOKEN в Authorization: Bearer <token>.
Используется: learning_service (за завершение модулей), другие сервисы.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from points_service.db.dependencies import get_db_session
from points_service.models.points import UserPoints, PointsTransaction
from points_service.schemas.points import (
    InternalAwardRequest,
    InternalSpendRequest,
    InternalRefundRequest,
    InternalMutationResponse,
    TransactionSchema,
)
from points_service.utils.auth import InternalAuth

router = APIRouter(prefix="/points")


async def _ensure_user_row(db: AsyncSession, user_id: int):
    # Создаём запись кошелька при отсутствии (idempotent)
    await db.execute(
        text(
            """
            INSERT INTO user_points (user_id, balance)
            VALUES (:user_id, 0)
            ON CONFLICT (user_id) DO NOTHING
            """
        ),
        {"user_id": user_id},
    )


async def _get_locked_wallet(db: AsyncSession, user_id: int) -> UserPoints:
    await _ensure_user_row(db, user_id)
    res = await db.execute(
        select(UserPoints).where(UserPoints.user_id == user_id).with_for_update()
    )
    obj = res.scalar_one()
    return obj


async def _check_idempotency(db: AsyncSession, idempotency_key: str):
    res = await db.execute(
        select(PointsTransaction).where(PointsTransaction.idempotency_key == idempotency_key)
    )
    return res.scalar_one_or_none()


@router.post("/award", response_model=InternalMutationResponse, summary="Начислить SP")
async def award_points(
    data: InternalAwardRequest,
    _: bool = InternalAuth,
    db: AsyncSession = Depends(get_db_session),
):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")

    existing = await _check_idempotency(db, data.idempotency_key)
    if existing:
        bal_res = await db.execute(
            select(UserPoints.balance).where(UserPoints.user_id == existing.user_id)
        )
        balance = bal_res.scalar() or 0
        return InternalMutationResponse(
            success=True,
            balance=balance,
            transaction=TransactionSchema.model_validate(existing, from_attributes=True),
        )

    async with db.begin():
        wallet = await _get_locked_wallet(db, data.user_id)
        wallet.balance = wallet.balance + int(data.amount)

        t = PointsTransaction(
            user_id=data.user_id,
            delta=int(data.amount),
            type="award",
            reason=data.reason,
            source_service=data.source_service,
            reference_type=data.reference_type,
            reference_id=str(data.reference_id) if data.reference_id is not None else None,
            idempotency_key=data.idempotency_key,
        )
        db.add(t)

    await db.refresh(wallet)
    await db.refresh(t)
    return InternalMutationResponse(
        success=True,
        balance=wallet.balance,
        transaction=TransactionSchema.model_validate(t, from_attributes=True),
    )


@router.post("/spend", response_model=InternalMutationResponse, summary="Списать SP")
async def spend_points(
    data: InternalSpendRequest,
    _: bool = InternalAuth,
    db: AsyncSession = Depends(get_db_session),
):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")

    existing = await _check_idempotency(db, data.idempotency_key)
    if existing:
        bal_res = await db.execute(
            select(UserPoints.balance).where(UserPoints.user_id == existing.user_id)
        )
        balance = bal_res.scalar() or 0
        return InternalMutationResponse(
            success=True,
            balance=balance,
            transaction=TransactionSchema.model_validate(existing, from_attributes=True),
        )

    async with db.begin():
        wallet = await _get_locked_wallet(db, data.user_id)
        if wallet.balance < int(data.amount):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient balance")

        wallet.balance = wallet.balance - int(data.amount)

        t = PointsTransaction(
            user_id=data.user_id,
            delta=-int(data.amount),
            type="spend",
            reason=data.reason,
            source_service=data.source_service,
            reference_type=data.reference_type,
            reference_id=str(data.reference_id) if data.reference_id is not None else None,
            idempotency_key=data.idempotency_key,
        )
        db.add(t)

    await db.refresh(wallet)
    await db.refresh(t)
    return InternalMutationResponse(
        success=True,
        balance=wallet.balance,
        transaction=TransactionSchema.model_validate(t, from_attributes=True),
    )


@router.post("/refund", response_model=InternalMutationResponse, summary="Рефанд SP")
async def refund_points(
    data: InternalRefundRequest,
    _: bool = InternalAuth,
    db: AsyncSession = Depends(get_db_session),
):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")

    existing = await _check_idempotency(db, data.idempotency_key)
    if existing:
        bal_res = await db.execute(
            select(UserPoints.balance).where(UserPoints.user_id == existing.user_id)
        )
        balance = bal_res.scalar() or 0
        return InternalMutationResponse(
            success=True,
            balance=balance,
            transaction=TransactionSchema.model_validate(existing, from_attributes=True),
        )

    async with db.begin():
        wallet = await _get_locked_wallet(db, data.user_id)
        wallet.balance = wallet.balance + int(data.amount)

        t = PointsTransaction(
            user_id=data.user_id,
            delta=int(data.amount),
            type="refund",
            reason=data.reason,
            source_service=data.source_service,
            reference_type=data.reference_type,
            reference_id=str(data.reference_id) if data.reference_id is not None else None,
            idempotency_key=data.idempotency_key,
        )
        db.add(t)

    await db.refresh(wallet)
    await db.refresh(t)
    return InternalMutationResponse(
        success=True,
        balance=wallet.balance,
        transaction=TransactionSchema.model_validate(t, from_attributes=True),
    )
