import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Le front est servi sur la même origine que l'API grâce à ce proxy : le cookie
// de session obtenu sur /admin/ est donc envoyé avec les appels /api/, sans CORS.
export default defineConfig(({ command }) => ({
  plugins: [react()],
  // En build, les fichiers sont collectés par Django et servis par WhiteNoise
  // sous STATIC_URL : sans cette base, index.html les demanderait à la racine et
  // la production répondrait 404. En dev, Vite sert depuis la racine — appliquer
  // la même base y casserait toutes les routes.
  base: command === "build" ? "/static/" : "/",
  server: {
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
      "/media": { target: "http://localhost:8000", changeOrigin: true },
      "/admin": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
}));
