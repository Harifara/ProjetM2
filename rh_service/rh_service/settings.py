from pathlib import Path
from datetime import timedelta
from decouple import config
import os
import mimetypes

# === Répertoires de base ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Sécurité ===
SECRET_KEY = config("SECRET_KEY", default="rh_service_secret_key_123")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# === Applications installées ===
INSTALLED_APPS = [
    # Apps internes
    "rh",

    # Apps Django de base
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Extensions
    "corsheaders",
    "rest_framework",
    "django_filters",
]

# === Middleware ===
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === CORS (Cross-Origin Resource Sharing) ===
CORS_ALLOW_ALL_ORIGINS = True  # ⚠️ À restreindre en production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_EXPOSE_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["GET", "POST", "PATCH", "DELETE", "OPTIONS", "PUT"]

# === URLs / Templates / WSGI ===
ROOT_URLCONF = "rh_service.urls"
WSGI_APPLICATION = "rh_service.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# === Base de données ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="rh_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="rh_db"),  # pour Docker network
        "PORT": config("DB_PORT", default="5432"),
    }
}

# === Django REST Framework ===
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rh.authentication.KongJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# === JWT (authentification inter-services) ===
JWT_SECRET = config("JWT_SECRET", default="my_super_secret_key_123")
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "auth-service"
AUTH_SERVICE_URL = config("AUTH_SERVICE_URL", default="http://auth_service:8000")

# === Internationalisation ===
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Indian/Antananarivo"
USE_I18N = True
USE_TZ = True

# === Fichiers statiques et médias ===
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# 💡 URL absolue complète pour les médias (utilisable côté frontend)
MEDIA_FULL_URL = config("MEDIA_FULL_URL", default="http://localhost:9000")

# === Fallback par défaut pour les clés primaires ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === Fix pour fichiers JS et images en dev ===
if DEBUG:
    mimetypes.add_type("application/javascript", ".js", True)
