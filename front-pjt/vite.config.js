import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],

    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    server: {
        host: "0.0.0.0",
        port: 3000,
        proxy: {
            '/api/chatbot': {
                target: 'http://localhost:8000', // Django 서버 주소로 맞춰주세요
                changeOrigin: true,
                secure: false,
            },
        },
    },
    preview: {
        host: "0.0.0.0",
        port: 3000
    }
});