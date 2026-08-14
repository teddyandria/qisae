# CLAUDE.md — Point d'entrée agent

> Fichier chargé automatiquement à chaque session. **Garde-le court.**
> Il contient uniquement les règles non négociables + des pointeurs vers `/docs`.
> Tout le détail vit dans `/docs` (source de vérité, portable, éditable à la main).

## Le projet en une phrase

Plateforme web de **base de données casting** (figurants) : saisie des profils côté
back-office, recherche multicritères sur ~300 facettes (physique, sports, langues,
véhicules, compétences…). Voir `docs/project.md`.

## Stack

- **Backend** : Django + Django REST Framework, PostgreSQL. Monolithe.
- **Frontend** : React (types API générés, jamais devinés).
- **Recherche** : Postgres d'abord (index GIN, JSONB, M2M). Moteur externe
  (Meilisearch/Typesense) seulement si le volume le justifie — pas par défaut.

## Règles dures (ne jamais enfreindre)

1. **Ne sur-architecture pas.** Monolithe, pas de microservices. On ajoute de la
   complexité quand la douleur le justifie, pas avant.
2. **Suis les patterns déjà en place** dans le codebase plutôt que d'en inventer.
3. **Modèle de données** : toute facette *recherchable* est relationnelle
   (colonne / FK / M2M / through model). Le JSONB est réservé au libre non filtrable.
   **Jamais d'EAV.** Détail : `docs/data-model.md`.
4. **Contrat d'API généré, pas négocié** : le backend expose un schéma OpenAPI
   (drf-spectacular), le frontend en dérive ses types (openapi-typescript).
   Le front ne devine jamais la forme des données. Détail : `docs/api-contract.md`.
5. **Données personnelles + mineurs = sujet sensible.** Consentement, export,
   suppression, conservation. Rien qui contourne ces contraintes. Voir `docs/project.md`.
6. **Migrations** : jamais éditer une migration appliquée ; toujours en générer une nouvelle.
7. Avant de proposer une décision structurante, vérifier `docs/decisions/`.

## Où trouver quoi

| Besoin                                   | Fichier                        |
|------------------------------------------|--------------------------------|
| Contexte, périmètre, contraintes, RGPD   | `docs/project.md`              |
| Modéliser un champ (les 5 patterns)      | `docs/data-model.md`           |
| Coder côté Django/DRF/admin              | `docs/conventions-backend.md`  |
| Coder côté React                         | `docs/conventions-frontend.md` |
| Interface backend ↔ frontend             | `docs/api-contract.md`         |
| Pourquoi une décision a été prise        | `docs/decisions/`              |

## Conventions transverses

- Réponses et commits **en français**. Code et identifiants **en français** aussi
  (cohérent avec le domaine métier : `Profil`, `sports`, `niveau`…).
- Commits : format court impératif (`ajoute filtre par sport`, `corrige inline photos`).
- Pas de filler dans les explications : réponse directe, actionnable, incrémentale.