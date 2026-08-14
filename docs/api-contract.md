# Contrat d'API — OpenAPI, source de vérité

Ce fichier définit **l'interface entre le backend et le frontend**. C'est la pièce
qui empêche les deux côtés de diverger.

## Principe

> Le contrat d'API se **génère** depuis le backend, il ne se **négocie** pas.
> Le backend produit un schéma OpenAPI à partir de ses serializers ; le frontend
> en dérive ses types TypeScript. **Le front ne décrit jamais un endpoint à la main.**

Conséquence directe : quand le backend change la forme d'une donnée, le schéma
change, les types régénérés changent, et TypeScript casse au bon endroit côté front
*à la compilation*. La divergence devient impossible à ignorer, au lieu d'être un
bug découvert à l'exécution.

## Le pipeline

```
serializers DRF
      │  drf-spectacular
      ▼
openapi.yaml  ← fichier committé dans git (le contrat visible en revue)
      │  openapi-typescript
      ▼
frontend/src/api/types.ts  ← types consommés par React
```

On **commit `openapi.yaml`** : ainsi un changement de contrat apparaît noir sur
blanc dans le diff d'un commit, au lieu d'être invisible.

## Setup backend (drf-spectacular)

```bash
pip install drf-spectacular
```

```python
# config/settings.py
INSTALLED_APPS += ["drf_spectacular"]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Casting DB API",
    "VERSION": "0.1.0",
}
```

```python
# config/urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),  # UI de test
]
```

## Générer le schéma

```bash
# depuis backend/
python manage.py spectacular --file openapi.yaml
```

À lancer **à chaque fois qu'un serializer ou un endpoint change**. Le fichier
`openapi.yaml` produit est committé.

## Setup frontend (openapi-typescript)

```bash
# depuis frontend/
npm install -D openapi-typescript
npx openapi-typescript ../backend/openapi.yaml -o src/api/types.ts
```

Ça génère les types TS de tous les schémas et endpoints. Pour un client fetch
typé de bout en bout, `openapi-fetch` se branche sur ces types (optionnel, à
décider dans `conventions-frontend.md`).

Ajouter un script npm pour ne pas retaper la commande :

```json
// frontend/package.json
"scripts": {
  "gen:api": "openapi-typescript ../backend/openapi.yaml -o src/api/types.ts"
}
```

## La boucle de travail (règle d'or)

À chaque évolution de l'API, dans cet ordre :

1. Backend : modifier le serializer / la vue.
2. `python manage.py spectacular --file openapi.yaml` → régénère le schéma.
3. Commit (le diff du contrat est visible).
4. Frontend : `npm run gen:api` → régénère les types.
5. TypeScript signale les endroits du front à mettre à jour.

Jamais l'inverse. Le front ne devine pas, il consomme.

## Conventions d'API

- **Préfixe** : tout sous `/api/`.
- **Pagination** : activer la pagination DRF par défaut (`PageNumberPagination`
  ou `LimitOffsetPagination`) — la base de profils peut être grosse.
- **Recherche à facettes** : exposée via les query params de `django-filter`
  (`/api/profils/?profilsport__sport__nom=Tennis&profilsport__niveau__gte=3`).
  drf-spectacular documente ces params si le `FilterSet` est bien déclaré sur la vue.
- **Écriture ouverte au staff** (depuis `decisions/0001`, à la demande du client) :
  `POST` / `PATCH` / `DELETE` sur `/api/profils/` et `/api/photos/`. La lecture reste
  ouverte à tout compte connecté, l'écriture exige `is_staff`. L'admin Django reste
  le second chemin de saisie. L'auto-inscription publique, elle, reste hors périmètre.
- **Authentification par session** : le front est proxifié par Vite sur la même
  origine, il réutilise donc le cookie de session de l'admin — pas de CORS, pas de
  token. Les requêtes d'écriture doivent porter l'en-tête `X-CSRFToken` ; le cookie
  est posé par `/api/session/` et par la liste des profils.
- **Nommage** : ressources au pluriel (`/api/profils/`, `/api/sports/`).
- **Versionnage** : pas nécessaire tant qu'il y a un seul consommateur (ton front).
  On y pensera si une API publique arrive.

## À refuser

- Écrire ou modifier `src/api/types.ts` à la main (c'est généré).
- Décrire côté front une forme de réponse qui n'existe pas dans le schéma.
- Committer un changement de serializer sans régénérer `openapi.yaml`.
- Versionner l'API « au cas où » alors qu'il y a un seul consommateur.