# catalog_service/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Устанавливаем postgresql-client для pg_isready
ARG DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
    if [ -f /etc/apt/sources.list ]; then \
        sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list; \
    fi; \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources; \
    fi; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates; \
    update-ca-certificates; \
    apt-get install -y --no-install-recommends postgresql-client curl; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы (включая init_db.sh)
COPY . .

# Делаем скрипт исполняемым
RUN chmod +x /app/init_db.sh

# Команда по умолчанию
CMD ["sh", "-c", "./init_db.sh && python -m uvicorn catalog_service.main:app --host 0.0.0.0 --port 8001 --reload"]
