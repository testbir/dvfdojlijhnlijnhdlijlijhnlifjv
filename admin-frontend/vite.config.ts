// admin-frontend/vite.config.ts

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    watch: {
      usePolling: true,
    },
    proxy: {
      "/admin-api": {
        target: "http://localhost:8010",
        changeOrigin: true,
        // Исправленная функция rewrite, которая сохраняет trailing slash
        rewrite: (path) => {
          // Удаляем префикс /admin-api
          const newPath = path.replace(/^\/admin-api/, "");
          // Если путь пустой, возвращаем /
          return newPath || '/';
        },
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 3000,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})