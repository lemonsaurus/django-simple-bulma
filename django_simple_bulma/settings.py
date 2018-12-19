"""
This project ensures the pdoc does not fail. Without this,
pdoc will fail with django.core.exceptions.ImproperlyConfigured:
Requested settings, but settings are not configured.
"""

SECRET_KEY = "I'm sure there's a better way to do this..."
