# points_service/models/points.py

"""
Назначение: ORM-модели SP-кошелька и транзакций.
Используется: CRUD и ограничения целостности.
"""

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    UniqueConstraint,
    Index,
    CheckConstraint,
    func,
)
from points_service.core.base import Base


class UserPoints(Base):
    __tablename__ = "user_points"

    # user_id как PK, чтобы легко делать SELECT ... FOR UPDATE
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    balance = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_user_points_non_negative"),
    )


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    # delta может быть <0 (списание) или >0 (начисление)
    delta = Column(BigInteger, nullable=False)

    # Тип операции: award|spend|refund|adjust
    type = Column(String(20), nullable=False)
    reason = Column(String(255), nullable=True)

    source_service = Column(String(64), nullable=True)
    reference_type = Column(String(64), nullable=True)
    reference_id = Column(String(128), nullable=True)

    idempotency_key = Column(String(255), nullable=False, unique=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_pts_idempotency_key"),
        Index("ix_pts_user_created", "user_id", "created_at"),
    )
