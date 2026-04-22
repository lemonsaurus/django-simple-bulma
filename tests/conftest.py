"""Test configuration for django-simple-bulma tests."""

import os

import django
from django.conf import settings


def pytest_configure() -> None:
    """Configure Django for testing."""
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
        django.setup()

    # Playwright's event loop stays alive during test teardown, which
    # otherwise trips Django's SynchronousOnlyOperation guard when the
    # test database is torn down. The DB work itself is safe; we're just
    # telling Django we know what we're doing.
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
