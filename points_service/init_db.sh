#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up!"

export PGPASSWORD="$POSTGRES_PASSWORD"

# 1) Создать БД если нет
if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -lqt \
  | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; then
  echo "Database $POSTGRES_DB already exists"
else
  echo "Creating database $POSTGRES_DB..."
  createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB"
fi

# 2) Применить модельные таблицы
python - <<'PYCODE'
import asyncio
from points_service.db.init_db import init_db
asyncio.run(init_db())
PYCODE

echo "DB ready. Starting app..."
