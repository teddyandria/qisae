# 0004 — Stockage des photos sur Cloudflare R2

**Date** : 2026-08-15
**Statut** : accepté

## Contexte

Le service Render gratuit exécute l'application dans un conteneur recréé à chaque
déploiement : son disque est donc éphémère. Les photos uploadées via le formulaire,
comme les images du jeu de démonstration, disparaissaient au déploiement suivant —
la base Neon gardait les enregistrements `Photo`, mais plus aucun fichier ne
correspondait, d'où des vignettes vides en production.

## Décision

Les fichiers médias sont stockés sur **Cloudflare R2** (S3-compatible) en production,
via `django-storages`. Le disque local reste utilisé en développement — bascule
automatique selon la présence des variables `R2_*`.

## Conséquences

- `STORAGES["default"]` pointe vers `storages.backends.s3.S3Storage` uniquement si
  `R2_BUCKET` est définie ; sinon `FileSystemStorage` inchangé.
- `PhotoSerializer.url` continue de lire `image.url` sans modification : ce champ
  renvoie une URL relative avec le disque local, une URL absolue vers R2 avec S3Storage
  — les deux sont directement utilisables par le front.
- Le bucket R2 doit être configuré en **accès public** (ou domaine personnalisé) : ce
  ne sont pas des données sensibles à protéger par jeton, seulement des photos servies
  à un front authentifié par ailleurs.
- Free tier R2 : 10 Go de stockage, largement suffisant pour ce volume de photos.
  Nécessite une carte bancaire à l'inscription Cloudflare, sans prélèvement en dessous
  du seuil gratuit.

## Ce qui ne change pas

Uniquement le stockage des fichiers. Le jeu de démonstration reste régénérable par
`charger_demo`, la base de données reste sur Neon.
