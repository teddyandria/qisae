import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
RACINE = BASE_DIR.parent  # dépôt : contient backend/ et frontend/

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# En production, aucune valeur de repli : mieux vaut refuser de démarrer qu'exposer
# un secret connu de tous, ce dépôt étant public.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "" if not DEBUG else "dev-non-secrete")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY est obligatoire quand DJANGO_DEBUG=0."
    )
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Render expose le domaine du service ; on l'autorise sans avoir à le recopier.
_hote_render = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _hote_render:
    ALLOWED_HOSTS.append(_hote_render)

# Le front est servi par Vite sur :5173 et proxifie /api vers :8000. Le navigateur
# envoie donc `Origin: localhost:5173` sur les POST, alors que Django reçoit un Host
# réécrit en :8000 — sans cette liste, toute écriture est rejetée en 403 CSRF.
# En production, y déclarer l'origine publique du front.
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
if _hote_render:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_hote_render}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "casting",
]

# L'API sert des données personnelles : elle reste fermée. Le front est proxifié
# par Vite sur la même origine, il réutilise donc le cookie de session obtenu en
# se connectant à l'admin — pas besoin de CORS ni de gestion de token.
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,  # multiple de la grille planche-contact (4 colonnes)
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Casting DB API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Sert les fichiers statiques sans serveur web dédié : Django n'en sert aucun
    # quand DEBUG=False, et Render ne fournit pas de nginx sur le plan gratuit.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [_front] if (_front := RACINE / "frontend" / "dist").exists() else [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# En production, l'hébergeur fournit DATABASE_URL (Neon). En local, on retombe sur
# le service `db` de compose.yml : un `docker compose up -d` suffit, sans configuration.
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,  # exigé par Neon
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "qisae"),
            "USER": os.environ.get("POSTGRES_USER", "qisae"),
            # Repli de développement uniquement : en production DATABASE_URL est
            # fournie par l'hébergeur et cette branche n'est jamais atteinte.
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "qisae_dev"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Le front construit par Vite est collecté comme des statiques Django : une seule
# origine, donc cookies de session et CSRF fonctionnent sans configuration réseau.
_front = RACINE / "frontend" / "dist"
STATICFILES_DIRS = [_front] if _front.exists() else []
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Photos sur Cloudflare R2 si configuré : le disque de Render est effacé à chaque
# redéploiement (voir docs/decisions/0004), donc les fichiers uploadés par le
# formulaire (pas seulement le jeu de démo régénérable) doivent vivre ailleurs.
# Sans ces variables, on retombe sur le disque local — inchangé pour le développement.
AWS_STORAGE_BUCKET_NAME = os.environ.get("R2_BUCKET")
if AWS_STORAGE_BUCKET_NAME:
    AWS_ACCESS_KEY_ID = os.environ["R2_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["R2_SECRET_ACCESS_KEY"]
    AWS_S3_ENDPOINT_URL = os.environ["R2_ENDPOINT_URL"]  # https://<compte>.r2.cloudflarestorage.com
    AWS_S3_REGION_NAME = "auto"
    AWS_S3_ADDRESSING_STYLE = "virtual"
    AWS_DEFAULT_ACL = None  # R2 n'a pas d'ACL S3 ; le bucket doit être en accès public
    AWS_QUERYSTRING_AUTH = False  # URLs stables, sans jeton de signature à expiration
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=31536000, immutable"}

    # URL publique du bucket : le sous-domaine r2.dev fourni par Cloudflare, ou un
    # domaine personnalisé si tu en as attaché un au bucket.
    _domaine_r2 = os.environ.get("R2_DOMAINE_PUBLIC")
    if _domaine_r2:
        AWS_S3_CUSTOM_DOMAIN = _domaine_r2

    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}

# Derrière le proxy de Render, c'est cet en-tête qui indique le HTTPS réel.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
