#!/usr/bin/env bash
# Construction pour Render : front puis backend, dans cet ordre — `collectstatic`
# a besoin du `frontend/dist` produit juste avant.
set -o errexit

echo "→ Front (Vite)"
cd frontend
npm ci
npm run build
cd ..

echo "→ Backend (Django)"
pip install -r backend/requirements.txt
cd backend
python manage.py collectstatic --no-input
python manage.py migrate

# Référentiel du cahier des charges : idempotent, sans effet si déjà chargé.
python manage.py charger_referentiel

# Compte administrateur initial : le Shell de Render est payant, donc
# `createsuperuser` (interactif) est inutilisable. Sans variables, ne fait rien.
python manage.py creer_admin

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
