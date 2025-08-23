import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/.well-known': { target: 'http://localhost:8000', changeOrigin: true },
      '/oauth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        bypass(req) {
          // SPA только для браузерного GET на /oauth/authorize
          if (req.method === 'GET' && req.url === '/oauth/authorize') {
            return req.url
          }
        },
      },
    },
  },
})
