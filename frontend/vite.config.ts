// frontend/vite.config.ts

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Определяем, запущено ли приложение в Docker
const isDocker = process.env.DOCKER_ENV === 'true' || process.env.NODE_ENV === 'production'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true,
    },
    proxy: {
      "/auth-api": {
        // В Docker используем имя сервиса, локально - localhost
        target: isDocker ? "http://authservice:8000" : "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth-api/, ""),
      },
      "/catalog-api": {
        target: isDocker ? "http://catalogservice:8001" : "http://localhost:8001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/catalog-api/, ""),
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 5173,
  },
});