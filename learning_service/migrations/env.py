import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from core.base import Base  # импортируешь свой Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Берём URL из переменной окружения
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

if db_url:
    config.set_main_option("sqlalchemy.url", db_url)
