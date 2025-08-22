# id_service/db/base.py
from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Строгая схема имен — важно для Alembic и воспроизводимости миграций
naming_convention = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Базовый класс моделей SQLAlchemy с единым MetaData и конвенцией имен."""
    metadata = MetaData(naming_convention=naming_convention)

    def __repr__(self) -> str:
        mapper = self.__class__.__mapper__
        pk_cols = [c.key for c in mapper.primary_key]
        pk_vals = ", ".join(f"{k}={getattr(self, k)!r}" for k in pk_cols)
        return f"<{self.__class__.__name__} {pk_vals}>"
