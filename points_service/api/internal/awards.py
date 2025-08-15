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

UPSERT_AWARD_REFUND = text("""
WITH ins AS (
  INSERT INTO points_transactions
    (user_id, points_delta, type, reason, source_service, reference_type, reference_id, idempotency_key)
  VALUES (:u, :d, :t, :r, :ss, :rt, :ri, :ik)
  ON CONFLICT (idempotency_key) DO NOTHING
  RETURNING user_id, points_delta
),
upd AS (
  UPDATE user_points up
  SET balance = up.balance + ins.points_delta
  FROM ins
  WHERE up.user_id = ins.user_id
  RETURNING up.balance
)
SELECT COALESCE((SELECT balance FROM upd),
                (SELECT balance FROM user_points WHERE user_id=:u)) AS balance
""")

async def _ensure_wallet(db: AsyncSession, user_id: int):
    await db.execute(
        text("INSERT INTO user_points (user_id, balance) VALUES (:u, 0) ON CONFLICT (user_id) DO NOTHING"),
        {"u": user_id},
    )

async def _get_tx_by_key(db, ik: str, user_id: int) -> PointsTransaction:
    q = await db.execute(select(PointsTransaction).where(
        PointsTransaction.idempotency_key == ik,
        PointsTransaction.user_id == user_id
    ))
    return q.scalar_one()

@router.post("/award", response_model=InternalMutationResponse)
async def award_points(data: InternalAwardRequest, db: AsyncSession = Depends(get_db_session)):
    async with db.begin():
        await _ensure_wallet(db, data.user_id)
        res = await db.execute(UPSERT_AWARD_REFUND, {
            "u": data.user_id, "d": data.amount, "t": "award",
            "r": data.reason, "ss": data.source_service,
            "rt": data.reference_type, "ri": data.reference_id, "ik": data.idempotency_key
        })
        balance = int(res.scalar() or 0)
        tx = await _get_tx_by_key(db, data.idempotency_key)
    return InternalMutationResponse(
        success=True, balance=balance,
        transaction=TransactionSchema.model_validate(tx, from_attributes=True)
    )
    
@router.post("/spend", response_model=InternalMutationResponse)
async def spend_points(data: InternalSpendRequest, db: AsyncSession = Depends(get_db_session)):
    async with db.begin():
        await _ensure_wallet(db, data.user_id)

        # 1) Блокируем кошелёк
        await db.execute(text("SELECT 1 FROM user_points WHERE user_id=:u FOR UPDATE"), {"u": data.user_id})

        # 2) Идемпотентность
        existing = await db.execute(select(PointsTransaction).where(
            PointsTransaction.idempotency_key == data.idempotency_key
        ))
        tx = existing.scalar_one_or_none()
        if tx:
            bal_q = await db.execute(select(UserPoints.balance).where(UserPoints.user_id == data.user_id))
            return InternalMutationResponse(
                success=True, balance=int(bal_q.scalar() or 0),
                transaction=TransactionSchema.model_validate(tx, from_attributes=True)
            )

        # 3) Проверка средств под блокировкой
        bal_q = await db.execute(select(UserPoints.balance).where(UserPoints.user_id == data.user_id))
        bal = int(bal_q.scalar() or 0)
        if bal < data.amount:
            raise HTTPException(status_code=409, detail={"message": "insufficient balance"})

        # 4) Записываем транзакцию и обновляем баланс
        await db.execute(text("""
            INSERT INTO points_transactions
            (user_id, points_delta, type, reason, source_service, reference_type, reference_id, idempotency_key)
            VALUES (:u, :neg, 'spend', :r, :ss, :rt, :ri, :ik)
        """), {"u": data.user_id, "neg": -data.amount, "r": data.reason, "ss": data.source_service,
               "rt": data.reference_type, "ri": data.reference_id, "ik": data.idempotency_key})

        upd = await db.execute(text("UPDATE user_points SET balance = balance - :d WHERE user_id=:u RETURNING balance"),
                               {"u": data.user_id, "d": data.amount})
        balance = int(upd.scalar_one())

        # 5) Читаем вставленную транзакцию
        tx = await _get_tx_by_key(db, data.idempotency_key)

    return InternalMutationResponse(
        success=True, balance=balance,
        transaction=TransactionSchema.model_validate(tx, from_attributes=True)
    )
    
@router.post("/refund", response_model=InternalMutationResponse)
async def refund_points(data: InternalRefundRequest, db: AsyncSession = Depends(get_db_session)):
    async with db.begin():
        await _ensure_wallet(db, data.user_id)
        res = await db.execute(UPSERT_AWARD_REFUND, {
            "u": data.user_id, "d": data.amount, "t": "refund",
            "r": data.reason, "ss": data.source_service,
            "rt": data.reference_type, "ri": data.reference_id, "ik": data.idempotency_key
        })
        balance = int(res.scalar() or 0)
        tx = await _get_tx_by_key(db, data.idempotency_key)
    return InternalMutationResponse(
        success=True, balance=balance,
        transaction=TransactionSchema.model_validate(tx, from_attributes=True)
    )