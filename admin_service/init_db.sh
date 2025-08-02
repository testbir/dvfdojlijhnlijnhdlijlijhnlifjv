#!/bin/sh

echo "⏳ Проверка и создание базы данных: $POSTGRES_DB"

export PGPASSWORD="$POSTGRES_PASSWORD"

# Проверяем существование базы данных
DB_EXISTS=$(psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; echo $?)

if [ $DB_EXISTS -eq 0 ]; then
    echo "✅ База '$POSTGRES_DB' уже существует."
else
    echo "🆕 Создаём базу данных '$POSTGRES_DB'..."
    psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;"
    echo "✅ База данных '$POSTGRES_DB' создана."
fi