import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(import.meta.dirname, 'src') },
  },
  test: { environment: 'jsdom', setupFiles: ['./src/test/setup.ts'], globals: false },
  server: {
    port: 5173,
    // En desarrollo, /api se reenvía al backend: no hace falta CORS ni exponer URLs en el cliente.
    proxy: { '/api': 'http://localhost:8000' },
  },
})
