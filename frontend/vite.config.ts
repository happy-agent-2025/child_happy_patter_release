import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3007,
    host: 'localhost',
    strictPort: true, // 严格使用指定端口
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加UTF-8编码支持
            proxyReq.setHeader('Accept-Charset', 'utf-8');
          });
        }
      }
    }
  }
})