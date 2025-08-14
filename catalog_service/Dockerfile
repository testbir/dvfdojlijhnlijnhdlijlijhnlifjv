# catalog_service/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Устанавливаем postgresql-client для pg_isready
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы (включая init_db.sh)
COPY . .

# Делаем скрипт исполняемым
RUN chmod +x /app/init_db.sh

# Команда по умолчанию
CMD ["sh", "-c", "./init_db.sh && python -m uvicorn catalog_service.main:app --host 0.0.0.0 --port 8001 --reload"]

