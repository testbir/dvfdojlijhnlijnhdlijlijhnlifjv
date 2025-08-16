#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until psql -h "postgres_team" -U "postgres" -c '\q' 2>/dev/null; do
  sleep 1
done

echo "Creating databases if they don't exist..."

# Функция для создания БД если её нет
create_db_if_not_exists() {
    local db_name=$1
    psql -h "postgres_team" -U "postgres" -tc "SELECT 1 FROM pg_database WHERE datname = '$db_name'" | grep -q 1 || {
        echo "Creating database: $db_name"
        psql -h "postgres_team" -U "postgres" -c "CREATE DATABASE $db_name"
    }
}

# Создаем все необходимые БД
create_db_if_not_exists "team_platform"
create_db_if_not_exists "team_platform_auth"
create_db_if_not_exists "team_platform_admin"
create_db_if_not_exists "team_platform_catalog"
create_db_if_not_exists "team_platform_learning"
create_db_if_not_exists "team_platform_points"

echo "All databases created successfully!"