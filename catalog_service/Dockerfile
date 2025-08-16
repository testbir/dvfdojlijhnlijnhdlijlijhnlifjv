# catalog_service/Dockerfile

FROM python:3.11-slim

WORKDIR /catalog_service
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/catalog_service

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates postgresql-client curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# был неверный путь /app/init_db.sh
RUN sed -i 's/\r$//' ./init_db.sh && chmod +x ./init_db.sh

# опционально
RUN if [ -f pyproject.toml ] || [ -f setup.py ]; then pip install -e .; fi

CMD ["sh","-lc","set -e; ./init_db.sh; python -m uvicorn main:app --host 0.0.0.0 --port 8001"]
