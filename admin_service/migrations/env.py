# admin_service/migrations/env.py

import sys
import os

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context


# Добавляем путь к корню проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import settings
from db import Base
from models.admin import AdminUser  # Убедись, что модель действительно здесь

# Alembic config
config = context.config

# Настройка логгирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаинформация для автогенерации миграций
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    engine = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
