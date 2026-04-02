import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Tenant API: /{slug}/api/v1/...
      '^/[a-z0-9][a-z0-9\\-]*/api/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Super-admin API
      '/zoreza-admin/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Health check
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
