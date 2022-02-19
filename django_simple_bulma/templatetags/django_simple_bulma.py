"""
Template tags for the Django templating engine.

These are loaded when {% load django_simple_bulma %} is called.
"""

from django import template
from django.templatetags.static import static
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.simple_tag
def bulma(theme: str = "") -> SafeString:
    """Build static files required for Bulma."""
    from ..utils import (
        get_js_files,
        logger,
        themes,
    )
    if theme and theme not in themes:
        logger.warning(
            f"Theme '{theme}' does not match any of the detected themes: {', '.join(themes)}. "
            "Using default theme instead."
        )
        theme = ""

    # Build the html to include the stylesheet
    css = static(f"css/{theme + '_' if theme else ''}bulma.css")
    stylesheet_id = f"bulma-css-{theme}" if theme else "bulma-css"

    html = [
        f'<link rel="preload" href="{css}" as="style">',
        f'<link rel="stylesheet" href="{css}" id="{stylesheet_id}">',
    ]

    # Build html to include all the js files required.
    for js_file in map(static, get_js_files()):
        html.append(f'<script defer type="text/javascript" src="{js_file}"></script>')

    return mark_safe("\n".join(html))


@register.simple_tag
def font_awesome() -> SafeString:
    """
    Return the FontAwesome CDN link.

    Returns whatever kit has been specified in BULMA_SETTINGS.
    If none is provided, default to version 5.14.0
    """
    from ..utils import fontawesome_token
    if fontawesome_token:
        cdn_link = (
            '<link rel="preload" '
            f'href="https://kit.fontawesome.com/{fontawesome_token}.js" '
            'crossorigin="anonymous" '
            'as="script">\n'
            '<script defer '
            f'src="https://kit.fontawesome.com/{fontawesome_token}.js" '
            'crossorigin="anonymous"></script>'
        )
    else:
        cdn_link = (
            '<link rel="preload" '
            'href="https://use.fontawesome.com/releases/v5.14.0/css/all.css" '
            'integrity="sha384-HzLeBuhoNPvSl5KYnjx0BT+WB0QEEqLprO+NBkkk5gbc67FTaL7XIGa2w1L0Xbgc" '
            'crossorigin="anonymous" '
            'as="style">\n'
            '<link rel="stylesheet" '
            'href="https://use.fontawesome.com/releases/v5.14.0/css/all.css" '
            'integrity="sha384-HzLeBuhoNPvSl5KYnjx0BT+WB0QEEqLprO+NBkkk5gbc67FTaL7XIGa2w1L0Xbgc" '
            'crossorigin="anonymous">'
        )

    return mark_safe(cdn_link)
