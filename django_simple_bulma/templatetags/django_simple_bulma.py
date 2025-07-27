"""
Template tags for the Django templating engine.

These are loaded when {% load django_simple_bulma %} is called.
"""

from django import template
from django.templatetags.static import static
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.simple_tag
def bulma(theme: str = "", *, include_js: bool = True) -> SafeString:
    """Build static files required for Bulma.

    Parameters:
        theme:
            CSS theme to load. If the given theme can not be found, a warning
            will be logged and the library will fall back to the default theme.

    Keyword arguments:
        include_js:
            Whether to include directives to load Bulma's JavaScript resources
            in the result. Useful to prevent duplicate loading of JS when
            calling this tag more than once on the same resource.
    """
    from ..utils import (
        get_js_files,
        logger,
        get_themes,
    )
    themes = get_themes()
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
    if include_js:
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
    from django.conf import settings
    # Get fontawesome_token dynamically to support override_settings in tests
    try:
        if hasattr(settings, "BULMA_SETTINGS"):
            fontawesome_token = settings.BULMA_SETTINGS.get("fontawesome_token", "")
        else:
            fontawesome_token = ""
    except Exception:
        fontawesome_token = ""
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
