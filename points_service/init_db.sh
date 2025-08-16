#!/usr/bin/env sh
set -e
export PYTHONPATH=/points_service

# Стандартизируем PG-переменные
: "${PGHOST:=db}"
: "${PGPORT:=5432}"
: "${PGUSER:=postgres}"
: "${PGDATABASE:=team_platform_points}"

# Ждем Postgres
until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" >/dev/null 2>&1; do
  echo "waiting for postgres at ${PGHOST}:${PGPORT}..."
  sleep 1
done

# Если есть Alembic — мигрируем. Иначе — create_all как фолбэк.
if [ -f alembic.ini ] && [ -d migrations ]; then
  # Сконструируем DATABASE_URL, если не задан
  if [ -z "${DATABASE_URL:-}" ]; then
    if [ -n "${POSTGRES_PASSWORD:-}" ]; then
      export DATABASE_URL="postgresql+psycopg2://${PGUSER}:${POSTGRES_PASSWORD}@${PGHOST}:${PGPORT}/${PGDATABASE}"
    else
      export DATABASE_URL="postgresql+psycopg2://${PGUSER}@${PGHOST}:${PGPORT}/${PGDATABASE}"
    fi
  fi
  alembic upgrade head
else
  python - <<'PY'
import asyncio
from db.init_db import init_db
asyncio.run(init_db())
PY
fi
