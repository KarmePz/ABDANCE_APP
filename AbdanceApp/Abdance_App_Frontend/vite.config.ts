import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true, // permite acceder desde red externa (como ngrok)
    port: 5173, // puerto del frontend
    allowedHosts: [
      '45b8-190-183-84-54.ngrok-free.app', // frontend ngrok
      '959f-190-183-84-54.ngrok-free.app', // backend ngrok (por si haces llamadas cruzadas desde frontend)
    ],
    cors: true // opcional, útil si hacés peticiones a tu backend desde el frontend
  }
})
