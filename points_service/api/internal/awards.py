# points_service/api/internal/awards.py

"""
Назначение: внутренние эндпоинты для начисления/списания/рефанда SP.
Требует INTERNAL_TOKEN в Authorization: Bearer <token>.
Используется: learning_service (за завершение модулей), другие сервисы.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from points_service.db.dependencies import get_db_session
from points_service.models.points import UserPoints, PointsTransaction
from points_service.schemas.points import (
    InternalAwardRequest, InternalSpendRequest, InternalRefundRequest,
    InternalMutationResponse, TransactionSchema
)
from points_service.utils.auth import InternalAuth

router = APIRouter(prefix="/points", dependencies=[Depends(InternalAuth())])

async def _ensure_wallet(db: AsyncSession, user_id: int):
    await db.execute(
        text("INSERT INTO user_points (user_id, balance) VALUES (:u, 0) ON CONFLICT (user_id) DO NOTHING"),
        {"u": user_id},
    )

@router.post("/award", response_model=InternalMutationResponse)
async def award_points(data: InternalAwardRequest, db: AsyncSession = Depends(get_db_session)):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")
    async with db.begin():
        await _ensure_wallet(db, data.user_id)
        try:
            await db.execute(
                text("""INSERT INTO points_transactions
(user_id, points_delta, type, reason, source_service, reference_type, reference_id, idempotency_key)
VALUES (:u, :d, 'award', :r, :ss, :rt, :ri, :ik)"""),
                {"u": data.user_id, "d": data.amount, "r": data.reason, "ss": data.source_service,
                 "rt": data.reference_type, "ri": data.reference_id, "ik": data.idempotency_key},
            )
            await db.execute(text("UPDATE user_points SET balance = balance + :d WHERE user_id = :u"),
                             {"u": data.user_id, "d": data.amount})
        except Exception as e:
            if "unique" not in str(e).lower() and "duplicate" not in str(e).lower():
                raise
    bal = await db.execute(select(UserPoints.balance).where(UserPoints.user_id == data.user_id))
    tx  = await db.execute(select(PointsTransaction).where(PointsTransaction.idempotency_key == data.idempotency_key))
    return InternalMutationResponse(success=True, balance=int(bal.scalar() or 0),
                                    transaction=TransactionSchema.model_validate(tx.scalar_one(), from_attributes=True))

@router.post("/spend", response_model=InternalMutationResponse)
async def spend_points(data: InternalSpendRequest, db: AsyncSession = Depends(get_db_session)):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")
    async with db.begin():
        await _ensure_wallet(db, data.user_id)
        bal = await db.execute(select(UserPoints.balance).where(UserPoints.user_id == data.user_id))
        if int(bal.scalar() or 0) < data.amount:
            raise HTTPException(status_code=409, detail="insufficient balance")
        try:
            await db.execute(
                text("""INSERT INTO points_transactions
(user_id, points_delta, type, reason, source_service, reference_type, reference_id, idempotency_key)
VALUES (:u, :d, 'spend', :r, :ss, :rt, :ri, :ik)"""),
                {"u": data.user_id, "d": -data.amount, "r": data.reason, "ss": data.source_service,
                 "rt": data.reference_type, "ri": data.reference_id, "ik": data.idempotency_key},
            )
            await db.execute(text("UPDATE user_points SET balance = balance - :d WHERE user_id = :u"),
                             {"u": data.user_id, "d": data.amount})
        except Exception as e:
            if "unique" not in str(e).lower() and "duplicate" not in str(e).lower():
                raise
    bal2 = await db.execute(select(UserPoints.balance).where(UserPoints.user_id == data.user_id))
    tx   = await db.execute(select(PointsTransaction).where(PointsTransaction.idempotency_key == data.idempotency_key))
    return InternalMutationResponse(success=True, balance=int(bal2.scalar() or 0),
                                    transaction=TransactionSchema.model_validate(tx.scalar_one(), from_attributes=True))

@router.post("/refund", response_model=InternalMutationResponse)
async def refund_points(data: InternalRefundRequest, db: AsyncSession = Depends(get_db_session)):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")
    async with db.begin():
        await _ensure_wallet(db, data.user_id)
        try:
            await db.execute(
                text("""INSERT INTO points_transactions
(user_id, points_delta, type, reason, source_service, reference_type, reference_id, idempotency_key)
VALUES (:u, :d, 'refund', :r, :ss, :rt, :ri, :ik)"""),
                {"u": data.user_id, "d": data.amount, "r": data.reason, "ss": data.source_service,
                 "rt": data.reference_type, "ri": data.reference_id, "ik": data.idempotency_key},
            )
            await db.execute(text("UPDATE user_points SET balance = balance + :d WHERE user_id = :u"),
                             {"u": data.user_id, "d": data.amount})
        except Exception as e:
            if "unique" not in str(e).lower() and "duplicate" not in str(e).lower():
                raise
    bal = await db.execute(select(UserPoints.balance).where(UserPoints.user_id == data.user_id))
    tx  = await db.execute(select(PointsTransaction).where(PointsTransaction.idempotency_key == data.idempotency_key))
    return InternalMutationResponse(success=True, balance=int(bal.scalar() or 0),
                                    transaction=TransactionSchema.model_validate(tx.scalar_one(), from_attributes=True))
