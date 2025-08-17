# points_service/migrations/env.py

from logging.config import fileConfig
import os
from alembic import context
from sqlalchemy import engine_from_config, pool

from core.base import Base
from models import points  # импортируй модели, чтобы они зарегистрировались

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# брать URL из env и заменить +asyncpg
db_url = (os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url") or "").replace("+asyncpg","")
config.set_main_option("sqlalchemy.url", db_url)

def run_migrations_offline():
    context.configure(url=db_url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle":"named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
