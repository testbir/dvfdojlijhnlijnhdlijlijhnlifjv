# points_service/Dockerfile
FROM python:3.11-slim

WORKDIR /points_service

ARG DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
  sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list || true; \
  sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources || true; \
  apt-get update; \
  apt-get install -y --no-install-recommends ca-certificates postgresql-client; \
  rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/points_service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's/\r$//' ./init_db.sh && chmod +x ./init_db.sh

CMD ["sh","-lc","set -e; ./init_db.sh; python -m uvicorn main:app --host 0.0.0.0 --port 8003"]
