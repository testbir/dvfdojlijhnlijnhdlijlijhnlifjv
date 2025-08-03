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

# Копируем все файлы
COPY . .

# Создаем init_db.sh если его нет
RUN echo '#!/bin/bash\n\
set -e\n\
echo "⏳ Ожидание PostgreSQL..."\n\
export PGPASSWORD=$POSTGRES_PASSWORD\n\
until pg_isready -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-postgres}; do\n\
  echo "PostgreSQL недоступен - ждем..."\n\
  sleep 2\n\
done\n\
echo "✅ PostgreSQL готов!"\n\
echo "🚀 Запуск приложения..."' > /app/init_db.sh

# Делаем скрипт исполняемым
RUN chmod +x /app/init_db.sh

# Команда по умолчанию
CMD ["sh", "-c", "./init_db.sh && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"]