// frontend/src/api/catalogApi.ts

// API-клиент для catalog_service (порт 8001)
import { createApi } from "./axiosInstance";
export default createApi("/catalog-api");
