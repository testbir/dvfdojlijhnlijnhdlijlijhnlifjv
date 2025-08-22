# id_service/Dockerfile

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/id_service \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /id_service

# Install system dependencies
RUN set -eux; \
    if [ -f /etc/apt/sources.list ]; then \
      sed -i -E 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list; \
    fi; \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
      sed -i -E 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources; \
    fi; \
    printf 'Acquire::Retries "5";\n' > /etc/apt/apt.conf.d/80-retries; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl postgresql-client \
    || (sleep 2; apt-get update && apt-get install -y --no-install-recommends --fix-missing ca-certificates curl postgresql-client); \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make init script executable
RUN [ -f ./init_db.sh ] && sed -i 's/\r$//' ./init_db.sh && chmod +x ./init_db.sh || true

# Install package if setup.py exists
RUN if [ -f pyproject.toml ] || [ -f setup.py ]; then pip install -e .; fi

CMD ["sh","-lc","alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*'"]
