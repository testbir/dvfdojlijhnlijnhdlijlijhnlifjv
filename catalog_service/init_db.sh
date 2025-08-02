#!/bin/bash
set -e

echo "⏳ Проверка и создание базы данных: $POSTGRES_DB"

# Устанавливаем переменные
HOST=${POSTGRES_HOST:-postgres}
PORT=${POSTGRES_PORT:-5432}
USER=${POSTGRES_USER:-postgres}
DB=${POSTGRES_DB}

export PGPASSWORD=$POSTGRES_PASSWORD

# Ждем готовности PostgreSQL
echo "🔄 Ожидание готовности PostgreSQL..."
until pg_isready -h $HOST -p $PORT -U $USER; do
  echo "PostgreSQL недоступен - ждем..."
  sleep 2
done

echo "✅ PostgreSQL готов!"

# Проверка существования базы
DB_EXISTS=$(psql -h $HOST -U $USER -tAc "SELECT 1 FROM pg_database WHERE datname='${DB}'")

if [ "$DB_EXISTS" != "1" ]; then
  echo "📦 База данных '$DB' не существует. Создаю..."
  createdb -h $HOST -p $PORT -U $USER $DB
  echo "✅ База '$DB' успешно создана."
else
  echo "✅ База '$DB' уже существует."
fi

echo "🚀 Запуск приложения..."