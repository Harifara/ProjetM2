from pathlib import Path
from datetime import timedelta
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------
# Secret key & debug
# --------------------------
SECRET_KEY = config("SECRET_KEY", default="mahenina123")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost").split(",")

# --------------------------
# Applications & Middleware
# --------------------------
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "django_filters",
    "authentication",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "authentication.middleware.AuditLogMiddleware",  # Audit log
]

# --------------------------
# CORS configuration
# --------------------------
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default="True") == "True"
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default="True") == "True"
CORS_ALLOW_HEADERS = ["*"]
CORS_EXPOSE_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]

# --------------------------
# Templates
# --------------------------
ROOT_URLCONF = "auth_service.urls"
WSGI_APPLICATION = "auth_service.wsgi.application"

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

# --------------------------
# Database
# --------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="auth_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="auth_db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# --------------------------
# Auth / JWT
# --------------------------
AUTH_USER_MODEL = "authentication.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

SIMPLE_JWT = {
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("JWT_SECRET", default="my_super_secret_key_123"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # ✅ Pour Kong / JWT validation
    "ISSUER": "auth-service",
    
}

# --------------------------
# Internationalisation / statics
# --------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Indian/Antananarivo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
