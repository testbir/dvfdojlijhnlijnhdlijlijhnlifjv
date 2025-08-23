# build
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
ARG VITE_API_BASE=/idp
ARG VITE_CLIENT_ID=id_frontend
ENV VITE_API_BASE=$VITE_API_BASE
ENV VITE_CLIENT_ID=$VITE_CLIENT_ID
COPY . .
RUN npm run build

# serve
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# SPA fallback + кэш ассетов
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
