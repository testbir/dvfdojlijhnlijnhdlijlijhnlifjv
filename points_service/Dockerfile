# points_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/init_db.sh

CMD ["sh", "-c", "./init_db.sh && python -m uvicorn points_service.main:app --host 0.0.0.0 --port 8003"]
