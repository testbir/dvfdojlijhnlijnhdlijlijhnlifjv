#!/bin/sh
echo "Waiting for PostgreSQL..."
MAX_ATTEMPTS=60
ATTEMPT=0
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT+1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "PostgreSQL not available after $MAX_ATTEMPTS seconds, exiting."
        exit 1
    fi
    sleep 1
done

export PGPASSWORD="$POSTGRES_PASSWORD"

if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; then
    echo "Database $POSTGRES_DB exists"
else
    echo "Creating database $POSTGRES_DB..."
    createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB" || exit 1
fi
