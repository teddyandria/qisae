# 0002 — Styling en CSS Modules

**Date** : 2026-08-13
**Statut** : accepté

## Contexte

`conventions-frontend.md` laissait le styling ouvert (« Tailwind ou CSS Modules, au
choix — à figer dans un ADR le jour où on commence l'UI »). L'UI a commencé.

## Décision

**CSS Modules**, avec les tokens de `design.md` en variables CSS dans
`src/styles/tokens.css`.

Raison : la direction visuelle repose sur des valeurs très spécifiques (trois familles
typographiques, `border-radius: 0` global, overlay de grain, tracé animé du cercle de
select, palette fonctionnelle par famille de facettes). Ce sont des règles à écrire une
fois dans un fichier, pas des utilitaires à composer dans le JSX. Tailwind aurait ajouté
une configuration et une couche de traduction sans bénéfice ici.

## Conséquences

- Un `.module.css` par composant, à côté du `.tsx`.
- Les tokens vivent dans `tokens.css` et **uniquement** là : aucune valeur hexadécimale
  en dur dans un composant, pour que la direction visuelle reste modifiable d'un endroit.
- Pas de dépendance de styling supplémentaire.
