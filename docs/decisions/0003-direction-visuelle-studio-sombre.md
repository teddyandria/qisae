# 0003 — Bascule vers une direction visuelle sombre

**Date** : 2026-08-14
**Statut** : accepté
**Demandeur** : client
**Remplace** : la direction « Planche-contact » claire, validée sur maquette

## Contexte

La première direction visuelle reposait sur un fond studio clair et une retenue
maximale : une seule micro-interaction, aucune ombre marquée, aucun gradient. Elle a
été jugée **trop fade** à l'usage. La demande : une interface professionnelle, avec des
effets et des animations soignés mais sans excès, et une vraie ambiance « casting ».

## Décision

Bascule vers **« Studio »** : interface sombre d'outil professionnel, avec les comp
cards maintenues sur un support clair neutre.

Deux alternatives ont été écartées à l'arbitrage : un éditorial clair premium (plus
proche de l'existant, mais moins de rupture avec le « fade » reproché), et un plateau
bi-ton très contrasté (spectaculaire, mais fatigant sur une journée de travail et
susceptible de dater vite).

## Ce qui est conservé

La contrainte métier reste intacte : **les carnations doivent rester justes**. C'est ce
qui interdit un fond sombre derrière les portraits. Les comp cards gardent donc leur
support clair `#FBFBFA`, et aucun filtre n'est appliqué aux images. Le contraste
sombre/clair sert le propos : les visages deviennent le seul point lumineux de l'écran.

Sont également conservés : les angles nets, les trois familles typographiques, le
vocabulaire métier, la signature du cercle au chinagraphe.

## Ce qui change

- Palette inversée (fond `#14151A`), plus une barre d'en-tête persistante.
- L'accent est décliné en **quatre tokens** selon le support : un seul bleu ne peut pas
  être lisible à la fois en texte sur fond sombre, en texte sur carte claire et sous du
  texte blanc. Chaque valeur est calée sur un contraste mesuré.
- Les **ombres portées**, refusées dans l'ancienne direction, sont admises : sur fond
  sombre elles séparent les plans sans salir. Réservées au survol et à l'état select.
- Le mouvement passe de « une micro-interaction » à **trois primitives** partageant une
  courbe et deux durées uniques : cascade d'arrivée, fondu, respiration de chargement.

## Conséquences

- `design.md` est réécrit ; la version claire n'a plus cours.
- Tout écran ajouté doit utiliser les tokens de mouvement : aucune durée ni courbe ad hoc.
- Le contraste AA est un critère de recette, y compris pour les familles de facettes.
