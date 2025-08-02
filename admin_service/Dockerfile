# admin_service/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# 🎬 Устанавливаем FFmpeg для обработки видео
RUN apt-get update && apt-get install -y \
    ffmpeg \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x init_db.sh

CMD ["sh", "-c", "./init_db.sh && uvicorn main:app --host 0.0.0.0 --port 8002"]