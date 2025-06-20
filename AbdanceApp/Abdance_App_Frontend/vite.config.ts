import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    host: true, // si querés que sea accesible en la red (ngrok, etc)
    cors: true,
    allowedHosts: ['b95c-190-183-84-54.ngrok-free.app'],
  }
})
