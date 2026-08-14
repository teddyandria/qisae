import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { GardeSaisie } from "./components/GardeSaisie";
import { PageConnexion } from "./features/connexion/PageConnexion";
import { FicheProfil } from "./features/fiche/FicheProfil";
import { PageRecherche } from "./features/recherche/PageRecherche";
import { FormulaireProfil } from "./features/saisie/FormulaireProfil";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/recherche" replace />} />
          <Route path="/connexion" element={<PageConnexion />} />
          <Route path="/recherche" element={<PageRecherche />} />
          <Route
            path="/profils/nouveau"
            element={
              <GardeSaisie>
                <FormulaireProfil />
              </GardeSaisie>
            }
          />
          <Route
            path="/profils/:id/modifier"
            element={
              <GardeSaisie>
                <FormulaireProfil />
              </GardeSaisie>
            }
          />
          {/* Déclarée en dernier : la route statique /profils/nouveau doit primer. */}
          <Route path="/profils/:id" element={<FicheProfil />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
