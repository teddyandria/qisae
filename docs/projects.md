# Projet — Contexte & décisions

Fichier de référence sur *le quoi* et *le pourquoi*. Pour *le comment* du code,
voir les `conventions-*.md`. Pour la structure des données, voir `data-model.md`.

## 1. Le produit

Plateforme web permettant de **retrouver des profils** (figurants / talents) dans
une base de données via une **recherche multicritères très large** (~300 facettes).

Catégories de critères :
- Informations générales (identité, localisation, contact, langues, disponibilité)
- Physique (mensurations, cheveux, yeux, tatouages, lunettes…)
- Apparence / représentation recherchée (registres, apparences)
- Sports (collectifs / individuels) **+ niveau**
- Véhicules / permis / conduite (+ cascade)
- Compétences artistiques **+ niveau**
- Instruments **+ niveau**
- Langues **+ accent + niveau**
- Métiers / savoir-faire
- Compétences particulières
- Composition de groupe, mineurs
- Vêtements / costumes
- Géographie / mobilité
- Expérience de tournage
- Photos (portrait, pied, profil, avec/sans barbe…)

Le cœur de valeur du produit = **la qualité et la fluidité de la recherche à facettes**.

## 2. Périmètre — Phase 1

- **Saisie exclusivement côté back-office (admin).** Pas d'auto-inscription des
  figurants pour l'instant. → C'est ce qui justifie le choix Django (admin natif).
- Un seul type d'utilisateur : l'admin qui gère la base et cherche des profils.
- Photos : upload + affichage. (Traitements avancés = plus tard.)

**Hors périmètre Phase 1** (à ne pas coder sans validation explicite) :
auto-inscription publique, messagerie, workflow de booking, paiements,
notifications, app mobile.

> Tout ajout demandé par le client qui sort de ce périmètre = **scope creep** à
> tracer (impact devis). C'est le rôle du subagent PO.

## 3. Stack & décisions structurantes

| Décision                     | Choix                        | Raison courte                              |
|------------------------------|------------------------------|--------------------------------------------|
| Backend                      | Django + DRF                 | Admin natif = back-office quasi gratuit    |
| Base de données              | PostgreSQL                   | array / JSONB / index GIN pour le multicritère |
| Frontend                     | React                        | UI de recherche riche                      |
| Architecture                 | Monolithe                    | Solo freelance, pas de microservices       |
| Recherche                    | Postgres d'abord             | Moteur externe seulement si le volume l'exige |
| Contrat API                  | OpenAPI généré               | Évite la dérive back/front                 |

Détail et alternatives écartées : `docs/decisions/`.

## 4. Modèle de données — principe directeur

Chaque facette est classée dans **un des 5 patterns** (détaillés dans `data-model.md`) :

1. Scalaire simple → colonne sur `Profil`
2. Choix unique → `choices` ou FK de référence
3. Multi-valué sans attribut → `ManyToManyField`
4. Multi-valué **avec** attribut (sport+niveau, langue+accent+niveau) → **through model**
5. Photos → modèle séparé one-to-many

Règle d'or : **recherchable ⇒ relationnel**. JSONB uniquement pour le libre non filtrable.
**Jamais d'EAV** (table clé/valeur générique) — ingérable pour recherche, formulaires, admin.

## 5. RGPD & mineurs — contrainte sensible

On manipule des **données personnelles + photos**. À respecter dès la conception :
- Consentement, finalité, durée de conservation documentées.
- Capacité d'**export** et de **suppression** d'un profil (droit à l'effacement).
- Traçabilité des accès si la base grossit.

**Mineurs** : responsable légal, autorisations, disponibilités spécifiques.
C'est un sujet **juridique** autant que technique — ne jamais improviser une
solution qui contourne le consentement ou l'autorisation parentale. En cas de
doute sur une exigence légale, le signaler plutôt que de deviner.

## 6. Anti-patterns (à refuser)

- EAV / table clé-valeur générique pour les facettes.
- JSONB pour des champs qu'on voudra filtrer.
- Un modèle `Profil` à 300 colonnes.
- Microservices, file de messages, cache distribué « au cas où ».
- Front qui devine la forme de l'API au lieu de lire les types générés.
- Deux agents (back/front) qui inventent chacun un contrat différent.