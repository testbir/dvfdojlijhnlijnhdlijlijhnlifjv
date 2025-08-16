# admin_service/Dockerfile

FROM python:3.11-slim
WORKDIR /admin_service
ENV PYTHONPATH=/admin_service PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates ffmpeg postgresql-client \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN sed -i 's/\r$//' /admin_service/init_db.sh && chmod +x /admin_service/init_db.sh
CMD ["sh","-lc","set -e; ./init_db.sh; uvicorn main:app --host 0.0.0.0 --port 8002"]
