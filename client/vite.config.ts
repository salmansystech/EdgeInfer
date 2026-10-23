import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const proxy = {
  '/api': {
    target: process.env.API_PROXY_TARGET || 'http://localhost:5000',
    changeOrigin: true,
  }
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy,
  },
  preview: {
    host: true,
    port: 3000,
    proxy,
  }
})
