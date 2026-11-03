#!/usr/bin/env bash
# Lancé au démarrage du service, avant gunicorn : c'est le seul moment où les
# variables (DATABASE_URL, ADMIN_*…) sont garanties. Tout est idempotent, donc
# sans effet lors d'un simple redémarrage.
set -o errexit

cd backend
python manage.py migrate

# Référentiel du cahier des charges : idempotent, sans effet si déjà chargé.
python manage.py charger_referentiel

# Compte administrateur initial : le Shell de Render est payant, donc
# `createsuperuser` (interactif) est inutilisable. Sans variables, ne fait rien.
python manage.py creer_admin

# Suppression du jeu de démonstration : à activer une fois (SUPPRIMER_DEMO=1),
# puis retirer la variable. Le Shell de Render étant payant, il n'y a pas d'autre
# moyen de lancer une commande ponctuelle qu'un déploiement.
# Ne pas laisser CHARGER_DEMO=1 en même temps : le bloc suivant les recréerait
# aussitôt après suppression.
if [ "${SUPPRIMER_DEMO:-0}" = "1" ]; then
  echo "→ Suppression du jeu de démonstration"
  python manage.py charger_demo --reset
fi

# Jeu de démonstration, seulement si demandé (CHARGER_DEMO=1).
# --reparer-photos tourne à chaque déploiement : la commande de base saute la
# création si les profils DEMO-* existent déjà (idempotence), mais leurs photos
# peuvent avoir disparu entre-temps — disque Render effacé, ou bascule vers un
# nouveau stockage (R2). Sans dégât si tout est déjà en place.
if [ "${CHARGER_DEMO:-0}" = "1" ]; then
  echo "→ Jeu de démonstration"
  python manage.py charger_demo || true
  python manage.py charger_demo --reparer-photos
fi
