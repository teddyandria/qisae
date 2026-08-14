import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { api } from "../../api/client";

/** L'état de recherche vit dans l'URL : partageable, bookmarkable, retour navigateur. */
export function useRecherche() {
  const [params, setParams] = useSearchParams();

  const query = useQuery({
    queryKey: ["profils", params.toString()],
    queryFn: async ({ signal }) => {
      // Les paramètres à niveau sont répétables (?sport=Tennis:3&sport=Judo) :
      // on passe donc l'URLSearchParams tel quel plutôt qu'un objet aplati.
      const reponse = await fetch(`/api/profils/?${params.toString()}`, {
        signal,
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      });
      if (reponse.status === 403 || reponse.status === 401) {
        throw new Error("NON_AUTHENTIFIE");
      }
      if (!reponse.ok) throw new Error(`Erreur ${reponse.status}`);
      return (await reponse.json()) as {
        count: number;
        next: string | null;
        previous: string | null;
        results: import("../../api/client").ProfilListe[];
      };
    },
    placeholderData: keepPreviousData,
  });

  function valeurs(cle: string) {
    return params.getAll(cle);
  }

  function basculer(cle: string, valeur: string) {
    const suivants = new URLSearchParams(params);
    const actuelles = suivants.getAll(cle);
    suivants.delete(cle);
    for (const v of actuelles) if (v !== valeur) suivants.append(cle, v);
    if (!actuelles.includes(valeur)) suivants.append(cle, valeur);
    suivants.delete("page");
    setParams(suivants);
  }

  function definir(cle: string, valeur: string | null) {
    const suivants = new URLSearchParams(params);
    if (valeur === null || valeur === "") suivants.delete(cle);
    else suivants.set(cle, valeur);
    suivants.delete("page");
    setParams(suivants);
  }

  function retirer(cle: string, valeur?: string) {
    const suivants = new URLSearchParams(params);
    if (valeur === undefined) {
      suivants.delete(cle);
    } else {
      const restantes = suivants.getAll(cle).filter((v) => v !== valeur);
      suivants.delete(cle);
      for (const v of restantes) suivants.append(cle, v);
    }
    setParams(suivants);
  }

  function toutEffacer() {
    setParams(new URLSearchParams());
  }

  function allerPage(numero: number) {
    const suivants = new URLSearchParams(params);
    if (numero <= 1) suivants.delete("page");
    else suivants.set("page", String(numero));
    setParams(suivants);
  }

  const page = Number(params.get("page") ?? 1);

  return { query, params, valeurs, basculer, definir, retirer, toutEffacer, page, allerPage };
}

/** Référentiels du rail de filtres — listes stables, mises en cache longuement. */
export function useReferentiel<T>(chemin: string) {
  return useQuery({
    queryKey: ["referentiel", chemin],
    queryFn: async () => {
      const reponse = await fetch(`/api${chemin}`, {
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      });
      if (!reponse.ok) throw new Error(`Erreur ${reponse.status}`);
      return (await reponse.json()) as T[];
    },
    staleTime: 60 * 60 * 1000,
    retry: false,
  });
}

export { api };
