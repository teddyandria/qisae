---
name: tests-sqlite-sans-docker
description: Quand Postgres/Docker est éteint, tester via /tmp/settings_test.py (SQLite mémoire) — mais jamais pour la recherche à facettes
metadata:
  type: feedback
---

Quand Docker n'est pas lancé, exécuter les vérifications avec :
`PYTHONPATH=<repo>/backend:/tmp DJANGO_SETTINGS_MODULE=settings_test .venv/bin/python ...`
(`/tmp/settings_test.py` hérite de `config.settings`, SQLite en mémoire).
`makemigrations` n'a pas besoin de base : le générer avec les settings normaux.

**Why:** l'utilisateur veut des vérifications réellement exécutées, pas supposées.
Mais `conventions-backend.md` interdit SQLite pour la recherche à facettes (ni GIN,
ni JSONB indexable, ni pg_trgm/unaccent) : le comportement observé ne serait pas
celui de la production.

**How to apply:** SQLite convient pour migrations, serializers, droits DRF, commandes
de management. Dès qu'un test porte sur les filtres/index Postgres, demander à lancer
Docker plutôt que de valider sur SQLite.
