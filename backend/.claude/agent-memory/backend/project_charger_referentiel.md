---
name: charger-referentiel-idempotence
description: charger_referentiel tourne à chaque déploiement Render — il amorce les listes mais ne doit jamais écraser une saisie admin
metadata:
  type: project
---

`casting/management/commands/charger_referentiel.py` s'exécute **à chaque déploiement
sur Render**. Il amorce les tables de référence, il ne fait pas autorité sur leur contenu.

**Why:** les listes sont éditables dans l'admin. Une commande qui réapplique ses valeurs
en dur écraserait silencieusement, à chaque déploiement, le travail de l'utilisateur.

**How to apply:** tout ajout à cette commande doit être idempotent *et* non destructif :
`get_or_create` pour les créations, et pour les relations, ne rattacher que si la
relation est encore **vide** (ex. `if accent.langues.exists(): continue`) — pas de
`.set()` inconditionnel. Voir [[accents-langues-nuance-metier]].
