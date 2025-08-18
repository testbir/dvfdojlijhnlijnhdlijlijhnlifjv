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
      '/admin-api': {
        target: 'http://localhost:8010',
        changeOrigin: true,
        rewrite: (path) => {
          // режем и приводим к одному ведущему /
          const p = path.replace(/^\/admin-api\/?/, '/');
          return p === '' ? '/' : p;
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