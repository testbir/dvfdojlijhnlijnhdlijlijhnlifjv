# admin_service/Dockerfile

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates ffmpeg postgresql-client \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN sed -i 's/\r$//' /app/init_db.sh && chmod +x /app/init_db.sh
RUN if [ -f pyproject.toml ] || [ -f setup.py ]; then pip install -e .; fi

CMD ["sh","-lc","set -e; ./init_db.sh; uvicorn admin_service.main:app --host 0.0.0.0 --port 8002"]
