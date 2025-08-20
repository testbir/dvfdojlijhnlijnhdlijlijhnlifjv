// frontend/src/api/authApi.ts


// API-клиент для auth_service (порт 8000)
import { createApi } from "./axiosInstance";
export const authApi = createApi("/auth-api");
