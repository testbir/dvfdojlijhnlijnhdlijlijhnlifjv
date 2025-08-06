// src/api/learningApi.ts
import { createApi } from "./axiosInstance";

export default createApi("/catalog-api"); // тот же прокси, если learning-эндпоинты лежат там же
// или '/learning-api', если в docker-compose появится отдельный сервис
