"""
Template tags for the Django templating engine.

These are loaded when {% load django_simple_bulma %} is called.
"""

from django import template
from django.templatetags.static import static
from django.utils.safestring import SafeString, mark_safe

from ..utils import get_js_files

register = template.Library()


@register.simple_tag
def bulma() -> SafeString:
    """Build static files required for Bulma."""
    # Build the html to include the stylesheet
    css = static("css/bulma.css")
    html = [f'<link rel="stylesheet" href="{css}">']

    # Build html to include all the js files required.
    for js_file in map(static, get_js_files()):
        html.append(f'<script defer type="text/javascript" src="{js_file}"></script>')

    return mark_safe("\n".join(html))  # noqa


@register.simple_tag
def font_awesome() -> SafeString:
    """
    Return the latest FontAwesome CDN link.

    Currently just returns 5.6.3, but will
    eventually return the latest version.
    """
    cdn_link = (
        '<link rel="stylesheet" '
        'href="https://use.fontawesome.com/releases/v5.6.3/css/all.css" '
        'integrity="sha384-UHRtZLI+pbxtHCWp1t77Bi1L4ZtiqrqD80Kn4Z8NTSRyMA2Fd33n5dQ8lWUE00s/" '
        'crossorigin="anonymous">'
    )

    return mark_safe(cdn_link)  # noqa
