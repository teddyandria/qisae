# 0001 — Saisie par formulaires dans le front (élargissement de périmètre)

**Date** : 2026-08-13
**Statut** : accepté
**Demandeur** : client

## Contexte

`projects.md` §2 pose que la saisie est **exclusivement back-office** en Phase 1, et
`api-contract.md` précise que les endpoints API sont **en lecture seule**, l'écriture
étant réservée à l'arrivée de l'auto-inscription. C'est ce choix qui justifiait Django
(admin natif = back-office quasi gratuit).

L'admin Django livré couvre déjà toute la saisie : tous les champs en fieldsets, les
7 inlines (dont sports+niveau, langues+accent et le dossier mineur), l'autocomplétion
sur les 18 référentiels, et l'accès réservé au compte administrateur.

## Décision

Le client demande malgré tout des **formulaires de saisie dans l'interface React**.
Décision prise en connaissance de l'alternative : l'admin Django reste en place et
fonctionnel, le front devient un second chemin de saisie.

## Conséquences

- L'API n'est plus en lecture seule : ouverture de `POST` / `PATCH` / `DELETE` sur
  les profils et les photos. `api-contract.md` §« Lecture seule côté front » ne décrit
  donc plus l'état réel du système.
- Écriture réservée aux comptes **staff** (`IsAdminUser`), lecture aux comptes
  authentifiés — le client a demandé que « lui seul » puisse saisir.
- Protection CSRF à gérer côté front (en-tête `X-CSRFToken`), là où une API en lecture
  seule n'en avait pas besoin.
- Les through models (sport+niveau, langue+niveau+accent, instrument, compétence
  artistique, véhicule) doivent être écrits en imbriqué : DRF ne le fait pas nativement,
  d'où un `create`/`update` explicite dans le serializer.
- **Deux chemins de saisie à maintenir** : toute évolution du modèle devra être
  répercutée dans l'admin *et* dans le formulaire React.

## Impact devis

Élargissement de périmètre par rapport à la Phase 1 contractualisée : ouverture de
l'API en écriture, formulaire multi-sections, upload de photos, et la maintenance
continue du doublon admin/front. À chiffrer séparément.
