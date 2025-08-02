# catalog_service/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Устанавливаем postgresql-client для pg_isready и curl для healthcheck
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Делаем скрипт исполняемым
RUN chmod +x init_db.sh

# Ждем PostgreSQL и запускаем приложение
CMD ["sh", "-c", "./init_db.sh && python -m uvicorn main:app --host 0.0.0.0 --port 8001"]