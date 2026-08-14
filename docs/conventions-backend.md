# Conventions backend — Django / DRF / admin

Règles de code côté backend. Pour la structure des données, voir `data-model.md`.
Pour l'interface avec le front, voir `api-contract.md`.

## Layout

Monolithe Django. Une app métier principale, découpée seulement si la douleur le justifie.

```
backend/
├── manage.py
├── config/                 # settings, urls, wsgi/asgi
│   ├── settings.py
│   └── urls.py
├── casting/                # app métier
│   ├── models.py
│   ├── admin.py
│   ├── serializers.py
│   ├── views.py
│   ├── filters.py          # logique de recherche à facettes
│   └── migrations/
└── requirements.txt        # ou pyproject.toml
```

## Modèles

- Nommage **en français**, cohérent avec le domaine (`Profil`, `sports`, `niveau`).
- Chaque champ suit un des 5 patterns de `data-model.md`. **Jamais d'EAV, jamais de JSONB recherchable.**
- FK vers une table de référence : `on_delete=models.PROTECT` (on ne veut pas
  qu'effacer un `Sport` supprime les liens). FK de composition (photos, liens) : `CASCADE`.
- `unique_together` sur les through models pour éviter les doublons profil/valeur.
- Toujours un `__str__` lisible (l'admin s'en sert partout).

## Base de données locale

Postgres tourne dans **Docker**, Django dans un **venv local**. On ne conteneurise pas
l'application en développement : rebuilds à chaque changement de dépendances, volumes
lents sur macOS et debugger moins direct, pour un bénéfice qui n'arrive qu'au déploiement.

```bash
docker compose up -d                 # Postgres — compose.yml, à la racine du repo
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

Les défauts de `compose.yml` et de `config/settings.py` sont alignés : aucune
configuration n'est nécessaire pour démarrer. Copier `.env.example` en `.env` sert
uniquement à surcharger (port 5432 déjà pris, mot de passe, etc.) — et `.env` n'est
lu automatiquement que par Compose, pas par le process Django.

- La **majeure de Postgres est épinglée** dans `compose.yml` : elle doit rester alignée
  sur la production. Ne pas basculer sur `latest`.
- `docker compose down -v` **détruit les données** — c'est le moyen de repartir d'une
  base vierge quand une migration part de travers. Sans `-v`, le volume survit.
- Ne jamais développer la recherche à facettes sur SQLite : ni GIN, ni JSONB indexable,
  ni `pg_trgm`/`unaccent`. Le comportement observé ne serait pas celui de la production.

## Migrations

- Une migration par changement logique, nommée explicitement (`makemigrations casting -n ajoute_champ_accent`).
- **Ne jamais éditer une migration déjà appliquée** → en générer une nouvelle.
- Vérifier `makemigrations --check` avant de commit (pas de migration manquante).

## Admin — le back-office est le produit en Phase 1

La saisie se fait à 100 % ici, donc l'admin doit être réellement confortable.

- **Through models (pattern 4) → `TabularInline`** sur `ProfilAdmin`. C'est ce qui
  permet de saisir « tennis / confirmé » directement sur la fiche profil.
- **`autocomplete_fields`** pour toutes les FK vers tables de référence : sans ça,
  les listes déroulantes deviennent inutilisables dès qu'il y a beaucoup de valeurs.
  Nécessite un `search_fields` sur l'admin de la table référencée.
- `list_display` : les champs qu'on scanne (nom, prénom, ville, sexe, âge).
- `list_filter` : les facettes de tri rapide (sexe, département, booléens).
- `search_fields` : nom, prénom, nom d'artiste, email.
- Photos (pattern 5) → `TabularInline` avec aperçu miniature.

```python
from django.contrib import admin
from .models import Profil, ProfilSport, Photo, Sport

class ProfilSportInline(admin.TabularInline):
    model = ProfilSport
    extra = 1
    autocomplete_fields = ["sport"]

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ("prenom", "nom", "ville", "sexe")
    list_filter = ("sexe", "departement", "lunettes")
    search_fields = ("nom", "prenom", "nom_artiste", "email")
    autocomplete_fields = ("permis", "metiers")
    inlines = [ProfilSportInline, PhotoInline]

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    search_fields = ("nom",)     # requis pour autocomplete_fields ailleurs
```

## API — DRF

- Serializers explicites (pas de `fields = "__all__"` sur le modèle central : on
  contrôle ce qui sort, surtout avec des données personnelles).
- ViewSets + routers DRF pour le CRUD, `ReadOnly` là où le front ne fait que lire.
- **`drf-spectacular`** génère le schéma OpenAPI. C'est la source de vérité du contrat
  API — le front en dérive ses types. Ne jamais décrire un endpoint « à la main »
  côté front. Détail : `api-contract.md`.

## Recherche à facettes — le cœur technique

Utiliser **`django-filter`** (`FilterSet`) plutôt que du filtrage à la main dans les vues.

Subtilité importante des through models (le point qu'on avait signalé) :

- Contraindre **un même** lien (ex. « tennis ET niveau ≥ confirmé ») → tout dans
  **un seul `.filter()`**, sinon Django peut matcher deux lignes différentes :

  ```python
  Profil.objects.filter(
      profilsport__sport__nom="Tennis",
      profilsport__niveau__gte="3",
  )
  ```

- Exiger **plusieurs** valeurs distinctes (ex. « pratique le tennis ET le judo ») →
  **`.filter()` chaînés**, un par valeur :

  ```python
  Profil.objects.filter(profilsport__sport__nom="Tennis") \
                .filter(profilsport__sport__nom="Judo")
  ```

- Penser à `.distinct()` dès qu'un filtre traverse un M2M (jointures = doublons).

Index : ajouter un **index GIN** sur les champs de recherche intensive quand le
volume le justifie. Postgres reste la source de vérité ; on n'introduit un moteur
externe (Meilisearch/Typesense) que si la latence des facettes devient un problème
réel, pas par anticipation.

## Tests

Pragmatique : tester la logique de recherche (les filtres à facettes) et les
contraintes RGPD (export, suppression), pas le CRUD trivial généré par DRF.
`pytest-django`, factories légères.

## RGPD dans le code

- Prévoir un endpoint / une action admin d'**export** et de **suppression** d'un profil.
- Ne pas logger de données personnelles en clair.
- Voir `project.md` §5 pour les contraintes, notamment les mineurs.

## À refuser

- `fields = "__all__"` sur le serializer du profil (fuite de champs personnels).
- Filtrage de recherche écrit à la main dans les vues au lieu d'un `FilterSet`.
- Éditer une migration appliquée.
- Ajouter un moteur de recherche externe « pour être prêt » avant d'en avoir besoin.
- Décrire un endpoint côté front sans passer par le schéma OpenAPI généré.