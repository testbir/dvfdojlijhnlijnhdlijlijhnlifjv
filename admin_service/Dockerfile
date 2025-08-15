# admin_service/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# 🎬 Устанавливаем FFmpeg для обработки видео + PostgreSQL клиент
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
    apt-get install -y --no-install-recommends ffmpeg postgresql-client; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x init_db.sh

CMD ["sh", "-c", "./init_db.sh && uvicorn main:app --host 0.0.0.0 --port 8002"]
