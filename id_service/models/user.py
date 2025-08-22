# id_service/models/user.py
from __future__ import annotations

import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Логинные поля
    email = Column(String(255), nullable=False)          # храним в lower на уровне приложения
    username = Column(String(50), nullable=False)

    # Безопасность
    password_hash = Column(Text, nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    failed_login_attempts = Column(Integer, nullable=False, default=0)

    # Аудит
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_password_change_at = Column(DateTime(timezone=True), nullable=True)

    # Таймстемпы и soft-delete
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        # case-insensitive уникальность e-mail
        Index("ux_users_email_lower", func.lower(email), unique=True),
        Index("ux_users_username", "username", unique=True),
    )
