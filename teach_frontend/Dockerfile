# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код
COPY . .

# Открываем порт
EXPOSE 5173

# Запускаем dev сервер с настройками для Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]