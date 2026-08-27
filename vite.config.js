import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const apiPort = process.env.ATLAS_API_PORT || '8787';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          const normalized = id.replaceAll('\\\\', '/');
          if (normalized.includes('/src/data/') || normalized.includes('/data/processed/')) return 'atlas-data';
          if (normalized.includes('/node_modules/leaflet/') || normalized.includes('/node_modules/react-leaflet/')) return 'map-vendor';
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${apiPort}`,
        changeOrigin: true,
      },
    },
  },
});
