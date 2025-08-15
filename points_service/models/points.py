# points_service/models/points.py

"""
Назначение: ORM-модели SP-кошелька и транзакций.
Используется: CRUD и ограничения целостности.
"""

from sqlalchemy import UniqueConstraint, Column, Integer, BigInteger, String, DateTime, Index, CheckConstraint, func
from points_service.core.base import Base

class UserPoints(Base):
    __tablename__ = "user_points"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    balance = Column(BigInteger, nullable=False, default=0)
    __table_args__ = (
        CheckConstraint("balance >= 0", name="chk_balance_non_negative"),
    )
    
class PointsTransaction(Base):
    __tablename__ = "points_transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    points_delta = Column(BigInteger, nullable=False)
    type = Column(String(20), nullable=False)  # award|spend|refund|adjust
    reason = Column(String(255), nullable=True)
    source_service = Column(String(64), nullable=True)
    reference_type = Column(String(64), nullable=True)
    reference_id = Column(String(128), nullable=True)
    idempotency_key = Column(String(255), nullable=False, unique=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("points_delta <> 0", name="chk_points_delta_nonzero"),
        Index("ix_tx_user_created", "user_id", "created_at"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_tx_user_ik"),
    )