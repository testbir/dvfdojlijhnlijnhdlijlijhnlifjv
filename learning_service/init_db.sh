#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up!"

export PGPASSWORD="$POSTGRES_PASSWORD"

# 1) Создаём базу (если нужно)
if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -lqt \
     | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; then
  echo "Database $POSTGRES_DB exists"
else
  echo "Creating database $POSTGRES_DB"
  createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB"
fi


# 2) Миграции схемы learning
echo "Running alembic migrations..."
alembic upgrade head

# 2.1) Ждём, пока каталог создаст свои таблицы (regclass вернёт t, когда таблица появится)
echo "Waiting for catalog tables..."
until psql "host=$POSTGRES_HOST port=$POSTGRES_PORT dbname=$POSTGRES_DB user=$POSTGRES_USER password=$POSTGRES_PASSWORD" \
  -tAc "SELECT to_regclass('courses_course') IS NOT NULL OR to_regclass('catalog.courses_course') IS NOT NULL;" | grep -qi t; do
  echo "Catalog tables not ready yet..."
  sleep 2
done

# 3) VIEW (idempotent)
echo "Applying views..."
psql "host=$POSTGRES_HOST port=$POSTGRES_PORT dbname=$POSTGRES_DB user=$POSTGRES_USER password=$POSTGRES_PASSWORD" \
  -v ON_ERROR_STOP=1 \
  -f /app/db/views.sql


echo "Init done."


