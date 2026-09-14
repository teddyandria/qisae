# 0005 — Sauvegardes automatiques de la base et des photos

**Date** : 2026-09-15
**Statut** : accepté

## Contexte

L'état du système vit sur deux hébergements gratuits distincts : la base Postgres chez
**Neon** (données saisies : profils, liens à niveau, référentiels) et les fichiers image
chez **Cloudflare R2** (voir [0004](0004-stockage-photos-cloudflare-r2.md)). Aucun des
deux ne garantit de sauvegarde exploitable sur son offre gratuite : Neon conserve un
historique court, R2 n'a ni versioning ni corbeille activés par défaut.

Le risque n'est pas théorique. Deux incidents survenus pendant le développement ont
déjà détruit des fichiers :

- `charger_demo --reset` a supprimé des images en masse ;
- Django ne supprimant jamais les fichiers physiques, des correctifs successifs ont dû
  être écrits pour nettoyer les orphelins — une erreur dans l'autre sens aurait effacé
  des fichiers encore référencés.

Une suppression accidentelle de profils par l'administrateur (compte unique, aucun
garde-fou applicatif) produirait le même résultat, sans aucun moyen de retour arrière.
C'est le seul risque **irréversible** du projet : une panne de Render se répare par un
redéploiement, une perte de données ne se répare pas.

## Décision

Une sauvegarde **quotidienne automatique**, exécutée par **GitHub Actions** (gratuit sur
dépôt public), déposant ses archives dans un bucket R2 **dédié et séparé** de celui des
photos servies.

Deux flux distincts, dans un même workflow :

1. **Base** — `pg_dump` en format `custom` (`-Fc`, compressé, restaurable table par table
   avec `pg_restore`), horodaté, versé dans `base/` du bucket de sauvegarde.
2. **Photos** — copie **incrémentale** (`rclone sync`) du bucket photos vers `photos/` du
   bucket de sauvegarde. Seuls les fichiers nouveaux ou modifiés transitent : le coût et
   la durée restent proportionnels aux changements du jour, pas au volume total.

**Rétention** : 30 jours pour les dumps, appliquée par le workflow lui-même (suppression
des archives plus anciennes). Le point n'est pas de garder l'espace propre — c'est que la
valeur d'une sauvegarde tient à sa **profondeur d'historique** : une erreur de saisie
repérée trois jours plus tard n'est récupérable que si l'état d'avant existe encore.

Les photos ne sont pas soumises à rétention : `sync` maintient un miroir, sans suppression
côté destination (`--ignore-existing` non utilisé, mais pas de `--delete` non plus — voir
« Conséquences »).

## Alternatives écartées

- **S'en remettre aux snapshots Neon** — rétention trop courte sur l'offre gratuite, et
  aucune copie hors du fournisseur : une erreur de compte ou de facturation emporte la
  base et ses sauvegardes ensemble.
- **Sauvegarder depuis Render** — le plan gratuit n'a pas de tâche planifiée (`cron job`
  est un service payant) et pas de Shell. Le build est le seul point d'exécution, ce qui
  lierait la sauvegarde au déploiement : ni quotidienne, ni fiable.
- **Versioning R2** — répond à la suppression accidentelle de fichiers, mais pas à la perte
  de la base, et ne fournit pas de copie hors-bucket. Complémentaire, pas substituable.
- **Un second fournisseur pour la copie** (Backblaze, S3) — plus robuste en cas de
  défaillance Cloudflare, mais ajoute un compte, des identifiants et une facturation à
  surveiller. Écarté au titre de la règle « ne pas sur-architecturer » : le bucket séparé
  couvre le risque principal, qui est l'erreur humaine, pas la faillite de Cloudflare.

## Conséquences

- Le dépôt porte un workflow `.github/workflows/sauvegarde.yml`, déclenché par `schedule`
  (03:17 UTC) et manuellement (`workflow_dispatch`) pour tester sans attendre.
- Quatre secrets GitHub à renseigner : `DATABASE_URL`, `R2_ENDPOINT_URL`,
  `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, plus deux variables de bucket. Aucune de ces
  valeurs n'entre dans le dépôt — le dépôt est **public**.
- Le jeton R2 utilisé doit pouvoir **lire** le bucket photos et **écrire** le bucket de
  sauvegarde. Un jeton en lecture seule sur les photos évite qu'un défaut du workflow
  n'endommage les originaux.
- `rclone sync` est employé **sans `--delete`** côté destination : une suppression
  accidentelle dans le bucket photos ne doit pas se propager à la sauvegarde. La
  conséquence assumée est que la sauvegarde conserve des fichiers volontairement
  supprimés — c'est le comportement recherché pour une sauvegarde.
- `pg_dump` est épinglé en **version 17**, alignée sur `compose.yml` et sur Neon. Un client
  plus ancien que le serveur refuse de s'exécuter : c'est la panne la plus courante de ce
  type de workflow.
- La restauration n'est **pas** automatisée : elle est décrite dans
  `docs/exploitation.md`. Une restauration automatique est un risque en soi.

## Ce qui n'est pas couvert

- **La sauvegarde n'est pas vérifiée par une restauration réelle.** Un dump qui s'écrit
  sans erreur n'est pas une garantie de restaurabilité. Tant qu'une restauration n'a pas
  été jouée au moins une fois, le dispositif est présumé fonctionnel, pas démontré tel.
- Aucune alerte en cas d'échec silencieux : GitHub notifie l'échec d'un workflow par
  courriel au propriétaire du dépôt, ce qui constitue le seul signal.
