#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is up!"

export PGPASSWORD="$POSTGRES_PASSWORD"

# 1) Создаём базу, если её нет
if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -lqt \
     | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; then
    echo "Database $POSTGRES_DB already exists"
else
    echo "Creating database $POSTGRES_DB..."
    createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB"
    echo "Database created!"
fi

# 2) Применяем миграции Alembic только если папка alembic существует
if [ -d "alembic" ]; then
    echo "Applying database migrations..."
    alembic upgrade head
else
    echo "No alembic directory found, skipping migrations..."
fi

# 3) Создание таблиц только в development (если нужно)
if [ "$FASTAPI_ENV" = "development" ]; then
    echo "Creating missing tables from models (if any)..."
    # Исправленный импорт - используем относительный путь
    python - <<PYCODE
import sys
sys.path.append('/app')
try:
    from scripts.init_db_async import init_db
    import asyncio
    asyncio.run(init_db())
    print("Database initialization completed")
except ImportError as e:
    print(f"Could not import init_db_async: {e}")
    print("Skipping database initialization...")
except Exception as e:
    print(f"Database initialization failed: {e}")
    print("Continuing with application startup...")
PYCODE
fi

echo "Database setup completed!"