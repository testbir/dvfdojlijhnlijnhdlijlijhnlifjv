# points_service/Dockerfile
FROM python:3.11-slim
WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
  sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list || true; \
  sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources || true; \
  apt-get update; \
  apt-get install -y --no-install-recommends ca-certificates postgresql-client; \
  rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Починить переносы строк, дать права
RUN sed -i 's/\r$//' /app/init_db.sh && chmod +x /app/init_db.sh

# Если есть pyproject.toml или setup.py — установить пакет
RUN if [ -f pyproject.toml ] || [ -f setup.py ]; then pip install -e .; fi

CMD ["sh","-lc","set -e; ./init_db.sh; python -m uvicorn points_service.main:app --host 0.0.0.0 --port 8003"]
