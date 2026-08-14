# Conventions frontend — React

Règles de code côté frontend. Pour l'interface avec le backend, voir `api-contract.md`.
Pour le périmètre, voir `project.md`.

## Stack

- **React + Vite + TypeScript.**
- **Données** : TanStack Query (React Query) pour tout appel API — cache, états
  loading/erreur, refetch gérés. Pas de Redux : l'app est surtout de la lecture
  (recherche + consultation), Query + l'état d'URL suffisent largement.
- **Types API** : générés depuis le schéma OpenAPI, jamais écrits à la main.

Pas de sur-ingénierie : pas de state manager global, pas de couche d'abstraction
« au cas où ». On ajoute une lib quand une vraie douleur le justifie.

## Layout

```
frontend/
├── src/
│   ├── api/
│   │   ├── types.ts        # GÉNÉRÉ (openapi-typescript) — NE JAMAIS ÉDITER
│   │   └── client.ts       # client fetch typé (openapi-fetch)
│   ├── features/
│   │   └── recherche/      # le cœur : panneau de filtres + liste de résultats
│   │       ├── PanneauFiltres.tsx
│   │       ├── ResultatsRecherche.tsx
│   │       └── useRecherche.ts
│   ├── components/         # UI réutilisable (boutons, champs, carte profil)
│   ├── hooks/
│   └── App.tsx
├── package.json
└── openapi.yaml → généré côté backend, lu par le script gen:api
```

## Types générés (règle dure)

- `src/api/types.ts` est produit par `npm run gen:api` (voir `api-contract.md`).
  **On ne l'édite jamais.** Si un type manque, c'est le backend/serializer qu'on corrige.
- Utiliser `openapi-fetch` pour un client typé de bout en bout : les chemins, les
  query params et les réponses sont vérifiés par TypeScript contre le schéma.

```ts
// src/api/client.ts
import createClient from "openapi-fetch";
import type { paths } from "./types";

export const api = createClient<paths>({ baseUrl: "/api" });
```

## Recherche à facettes — le cœur de l'UI

C'est l'écran principal. Deux zones : un **panneau de filtres** (les facettes) et
une **liste de résultats**.

**L'état de recherche vit dans l'URL**, pas dans un state local. Raison : une
recherche devient partageable, bookmarkable, et le bouton retour du navigateur
fonctionne. Les query params de l'URL **reflètent** les query params de l'API
(`django-filter`), ce qui rend le mapping trivial.

```
/recherche?profilsport__sport__nom=Tennis&profilsport__niveau__gte=3&sexe=F
```

- Lire/écrire les filtres via `useSearchParams` (React Router) → source de vérité unique.
- **Debounce** les filtres texte (~300 ms) pour ne pas spammer l'API à chaque frappe.
- TanStack Query **keyé sur les params d'URL** : changer un filtre = nouvelle clé =
  refetch + cache automatique.
- Afficher explicitement les états *loading* / *vide* / *erreur* (une base de
  profils vide ou une requête lente, ça arrive).

```ts
// esquisse de useRecherche.ts
const [params] = useSearchParams();
const query = useQuery({
  queryKey: ["profils", params.toString()],
  queryFn: () => api.GET("/profils/", { params: { query: Object.fromEntries(params) } }),
});
```

## Composants

- Composants fonctionnels + hooks. Logique réutilisable → hook custom (`useRecherche`).
- Découper par **feature** (`features/recherche/`) plutôt que par type technique.
- Une carte profil affiche les infos clés + la photo portrait ; la fiche détaillée
  montre toutes les facettes et la galerie (pattern 5 côté données).

## Photos

- Afficher les miniatures en liste, la galerie complète sur la fiche.
- Prévoir un fallback (profil sans photo) et le lazy-loading des images.

## Styling

Pragmatique, non tranché ici : Tailwind ou CSS Modules, au choix — l'important est
la cohérence. À figer dans un ADR le jour où on commence l'UI, pas avant.

## À refuser

- Éditer `src/api/types.ts` (généré).
- Décrire une forme de réponse qui n'est pas dans le schéma OpenAPI.
- Mettre l'état de recherche dans un state local au lieu de l'URL.
- Ajouter Redux ou un state manager global pour cette app en lecture.
- Introduire une lib UI lourde avant d'en avoir un besoin réel.