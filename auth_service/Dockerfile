# auth_service/Dockerfile


FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && apt install -y postgresql-client && apt clean

COPY . .
RUN chmod +x init_db.sh

CMD ["sh", "-c", "./init_db.sh && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
