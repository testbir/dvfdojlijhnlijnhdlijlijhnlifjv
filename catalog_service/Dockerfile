# catalog_service/Dockerfile

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/catalog_service \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /catalog_service

RUN set -eux; \
    # переключим http->https где бы ни лежали источники
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

RUN [ -f ./init_db.sh ] && sed -i 's/\r$//' ./init_db.sh && chmod +x ./init_db.sh || true

RUN if [ -f pyproject.toml ] || [ -f setup.py ]; then pip install -e .; fi

CMD ["sh","-lc","set -e; ./init_db.sh; python -m uvicorn main:app --host 0.0.0.0 --port 8001"]
