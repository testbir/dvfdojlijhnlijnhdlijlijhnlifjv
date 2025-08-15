# learning_service/Dockerfile

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates postgresql-client \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN sed -i 's/\r$//' /app/init_db.sh && chmod +x /app/init_db.sh


CMD ["sh","-lc","set -e; ./init_db.sh; python -m uvicorn learning_service.main:app --host 0.0.0.0 --port 8002"]
