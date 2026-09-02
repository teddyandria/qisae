---
name: accents-langues-nuance-metier
description: Règle métier validée client — un accent d'origine (Italien, Maghrébin) se rattache au français/anglais, jamais à sa langue d'origine
metadata:
  type: project
---

`Accent.langues` (M2M, `related_name="accents"`, `blank=True`) dit **dans quelles
langues l'accent s'entend**, pas de quelle langue il vient. Décision validée par le
client (2026-09-02).

- Accent **régional** (Marseillais, Lyonnais, Parisien, Québécois, Belge, Suisse,
  Antillais, Africain francophone, Français standard) → français.
- Accent **d'origine** (Italien, Espagnol, Portugais, Maghrébin) → français + anglais.
  **Jamais** la langue éponyme : un Italien parlant italien n'a pas « l'accent italien ».
- Britannique / Américain → anglais.
- `langues` vide = accent **universel**, proposé pour toutes les langues par le front.

**Why:** le formulaire proposait « Marseillais » quand on choisissait « Anglais ».
La confusion naturelle est de rattacher « Italien » à la langue italienne — c'est
l'erreur exacte à ne pas commettre.

**How to apply:** en touchant `ACCENTS_LANGUES` dans `charger_referentiel.py`, à la
liste d'accents, ou au filtrage front des accents. Le filtre front est :
accents de la langue choisie ∪ accents sans langue. Voir [[charger-referentiel-idempotence]].
