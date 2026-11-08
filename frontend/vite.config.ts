import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Порт 3000 зафиксирован: этот адрес зарегистрирован как redirect_uri
// у Google/GitHub, и только он разрешён в CORS на бэкенде.
// strictPort не даёт Vite молча уехать на 3001, если 3000 занят.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    strictPort: true,
  },
})
