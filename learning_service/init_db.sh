#!/usr/bin/env sh
set -euo pipefail

: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_DB:=learning_db}"
: "${POSTGRES_HOST:=db}"
: "${POSTGRES_PORT:=5432}"

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  echo "waiting for postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
  sleep 1
done

# Alembic читает URL из env.py (через Settings), .env файлы не нужны в шелле
if [ -f alembic.ini ]; then
  alembic upgrade head
fi
