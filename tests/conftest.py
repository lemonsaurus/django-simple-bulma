"""Test configuration for django-simple-bulma tests."""

import os

import django
from django.conf import settings


def pytest_configure() -> None:
    """Configure Django for testing."""
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
        django.setup()
