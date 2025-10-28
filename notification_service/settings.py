import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', 'mahenina123')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [
    'localhost',                 # pour accès local via navigateur
    '127.0.0.1',                 # idem
    'auth_service',
    'rh_service',
    'stock_service',
    'coordinateur_service',
    'finance_service',
    'notification_service',
    '*',                          # optionnel pour dev, autorise toutes les requêtes
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_results',
    'notification',  # ton app
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='notification_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='notification_db'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Celery config
CELERY_BROKER_URL = config('REDIS_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
