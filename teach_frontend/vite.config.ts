// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const inDocker = process.env.DOCKER_ENV === 'true'
const tgt = (name: string, port: number) =>
  inDocker ? `http://${name}:${port}` : `http://localhost:${port}`

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth-api': {
        target: tgt('authservice', 8000),
        changeOrigin: true,
        rewrite: p => p.replace(/^\/auth-api/, ''),
      },
      '/catalog-api': {
        target: tgt('catalogservice', 8001),
        changeOrigin: true,
        rewrite: p => p.replace(/^\/catalog-api/, ''),
      },
      '/learning-api': {
        target: tgt('learningservice', 8002), // внутренний порт, снаружи проброшен как 8004
        changeOrigin: true,
        rewrite: p => p.replace(/^\/learning-api/, ''),
      },
      '/points-api': {
        target: tgt('pointsservice', 8003),
        changeOrigin: true,
        rewrite: p => p.replace(/^\/points-api/, ''),
      },
    },
  },
})
