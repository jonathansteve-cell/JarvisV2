import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig} from 'vite';

// The Jarvis V2 Python backend (dashboard/server.py). Override with
// JARVIS_API_URL if you run it on another machine or port.
const BACKEND = process.env.JARVIS_API_URL || 'http://127.0.0.1:8765';

export default defineConfig(() => {
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 3000,
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modify—file watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
      // Disable file watching when DISABLE_HMR is true to save CPU during agent edits.
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
      // Dev-only: the UI calls relative /api/* paths, so `npm run dev` talks to
      // the real Python backend. In production the Python server serves ui/dist
      // directly and no proxy is involved.
      proxy: {
        '/api': {
          target: BACKEND,
          changeOrigin: true,
        },
      },
    },
  };
});
