import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const BACKEND_URL = "http://localhost:8000"

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Use a wildcard to proxy all API calls to the backend
      "/api": {
        target: BACKEND_URL,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
})
