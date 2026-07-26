import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const DEV_PORT = 5173;

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: DEV_PORT,
  },
  preview: {
    host: '0.0.0.0',
    port: DEV_PORT,
  },
});
