#!/usr/bin/env bash
# Construction de l'image : front puis backend, dans cet ordre — `collectstatic`
# a besoin du `frontend/dist` produit juste avant.
#
# Rien ici ne touche à la base : les variables du service ne sont pas garanties
# pendant le build (Railway). Migrations et chargements sont dans deploiement.sh,
# lancé au démarrage.
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
