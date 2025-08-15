# catalog_service/ale


import os, sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from catalog_service.core.base import Base  # путь к вашему Base
target_metadata = Base.metadata

from catalog_service.core.base import Base  # аналогично для других сервисов

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Добавляем каталог сервиса в PYTHONPATH
sys.path.insert(0, os.environ.get("PYTHONPATH", "/app"))

# Alembic Config object
config = context.config

# Подставляем DATABASE_URL из окружения
if os.getenv("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Логгирование Alembic
if config.config_file_name:
    fileConfig(config.config_file_name)

# Импортируем Base из пакета сервиса
from catalog_service.core.base import Base
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
