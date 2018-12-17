"""
A file used by Django in order to link this app
to the main project.
"""

from django.apps import AppConfig


class DjangoSimpleBulmaConfig(AppConfig):
    """
    The app config object for this app.

    Required to be able to add the app to
    INSTALLED_APPS in the Django settings.py file.
    """

    name = "django_simple_bulma"
