"""Django settings for django-simple-bulma tests."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

SECRET_KEY = "test-secret-key-not-for-production"

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django_simple_bulma",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "test_static"

STATICFILES_DIRS = [
    BASE_DIR / "test_static_files",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django_simple_bulma.finders.SimpleBulmaFinder",
]

# Bulma settings for testing
BULMA_SETTINGS = {
    "extensions": ["bulma-tooltip", "bulma-calendar"],
    "variables": {"primary": "#007bff", "family-primary": "Arial"},
    "alt_variables": {"primary": "#ff6b6b", "family-primary": "Helvetica"},
    "output_style": "compressed",
    "fontawesome_token": "abc123def456",
    "custom_scss": ["test_styles/custom.scss"],
}

USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
