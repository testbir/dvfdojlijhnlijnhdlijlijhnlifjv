# points_service/api/public/balance.py

"""
Назначение: публичные (пользовательские) эндпоинты:
 - GET баланс текущего пользователя
 - GET список его транзакций (пагинация)
Используется: фронтом "My Space / My Learning" и т.п.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from db.dependencies import get_db_session
from models.points import UserPoints, PointsTransaction
from schemas.points import BalanceResponse, TransactionsListResponse, TransactionSchema
from utils.auth import get_current_user_id

router = APIRouter(prefix="/points")

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(UserPoints.balance).where(UserPoints.user_id == user_id))
    return BalanceResponse(balance=int(res.scalar() or 0))

@router.get("/transactions", response_model=TransactionsListResponse)
async def list_transactions(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    total_q = await db.execute(select(func.count(PointsTransaction.id)).where(PointsTransaction.user_id == user_id))
    total = int(total_q.scalar() or 0)
    res = await db.execute(
        select(PointsTransaction)
        .where(PointsTransaction.user_id == user_id)
        .order_by(PointsTransaction.created_at.desc(), PointsTransaction.id.desc())
        .limit(limit).offset(offset)
    )
    items = res.scalars().all()
    return TransactionsListResponse(
        items=[TransactionSchema.model_validate(i, from_attributes=True) for i in items],
        total=total, limit=limit, offset=offset,
    )
