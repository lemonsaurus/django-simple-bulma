"""
This project ensures the pdoc does not fail. Without this,
pdoc will fail with django.core.exceptions.ImproperlyConfigured:
Requested settings, but settings are not configured.
"""

SECRET_KEY = 'It is very stupid that I need to create this file just to get pdoc working'
DEBUG = True

# Customizing Bulma
BULMA_SETTINGS = {
    "extensions": [
        "bulma-accordion",
        "bulma-calendar"
    ],
    "variables": {
        "primary": "#000000",
        "size-1": "6rem"
    }
}
