import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: false,
    watch: {
      usePolling: true
    },
    proxy: {
      '/api': {
        target: 'http://192.168.39.196:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/ws': {
        target: 'ws://192.168.39.196:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: false
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    minify: 'terser',
    target: 'esnext'
  }
})
