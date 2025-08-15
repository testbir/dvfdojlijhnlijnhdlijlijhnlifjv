#!/usr/bin/env sh
set -e
export PYTHONPATH=/app

: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_DB:=team_platform}"
: "${POSTGRES_HOST:=db}"
: "${POSTGRES_PORT:=5432}"

# ожидание БД
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
  sleep 1
done

# миграции
if [ -f manage.py ]; then
  python manage.py migrate
fi

if command -v alembic >/dev/null 2>&1 && [ -f alembic.ini ]; then
  alembic upgrade head
fi
