#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is up!"

export PGPASSWORD="$POSTGRES_PASSWORD"

# create DB if not exists
if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -lqt \
     | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; then
    echo "Database $POSTGRES_DB already exists"
else
    echo "Creating database $POSTGRES_DB..."
    createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB"
    echo "Database created!"
fi

python - <<PYCODE
import sys, asyncio
sys.path.append('/app')
from learning_service.db.init_db import init_db
asyncio.run(init_db())
print("DB init done")
PYCODE

echo "Database setup completed!"
