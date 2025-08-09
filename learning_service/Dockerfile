# learning_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# postgres client для pg_isready
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# права на init
RUN chmod +x /app/init_db.sh

# старт: ждём БД, миграции, создаём VIEW, запускаем uvicorn
CMD ["sh", "-c", "./init_db.sh && python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload"]

