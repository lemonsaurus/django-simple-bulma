"""Playwright visual end-to-end tests.

Renders a page that uses a handful of Bulma components, drives a real
Chromium browser against it, and asserts on computed styles. Catches
the class of regression where generated CSS looks right in isolation
but fails to actually apply in a browser.

Tightens what we can assert about customization behaviour as the
BULMA_SETTINGS cascade becomes more trustworthy (see #126 / #127).

Run locally:
    uv run playwright install chromium
    uv run pytest tests/test_e2e.py
"""

import os
from pathlib import Path

import pytest
from django.core.management import call_command

# Playwright's event loop stays alive during test teardown, which otherwise
# trips Django's SynchronousOnlyOperation guard when the test database is
# torn down. Scoped here (not in conftest) so non-e2e tests run with the
# guard intact.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

SCREENSHOT_DIR = Path(__file__).resolve().parent / "_artifacts"


def _rgb(value: str) -> tuple[int, int, int]:
    """Parse a CSS rgb()/rgba() string into an (r, g, b) tuple."""
    stripped = value.strip().removeprefix("rgb(").removeprefix("rgba(").rstrip(")")
    parts = [int(p.strip()) for p in stripped.split(",")[:3]]
    return (parts[0], parts[1], parts[2])


@pytest.fixture(scope="module")
def collected_static(django_db_setup, django_db_blocker) -> None:  # noqa: ARG001
    """Run collectstatic once per module so Django can serve Bulma CSS/JS."""
    with django_db_blocker.unblock():
        call_command("collectstatic", "--noinput", verbosity=0)


@pytest.fixture(autouse=True)
def _artifacts_dir() -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def test_bulma_css_reaches_the_browser(
    live_server, page, collected_static  # noqa: ARG001
) -> None:
    """Bulma must actually style components, not just ship bytes."""
    page.goto(live_server.url)

    button = page.get_by_test_id("primary-button")
    background = button.evaluate("el => getComputedStyle(el).backgroundColor")

    # An unstyled button on a blank page renders as the browser's native
    # button chrome — a light grey. Any of Bulma's primary shades (default
    # turquoise, or a user override) will be saturated and non-grey. If
    # CSS never loaded this assertion is what catches it.
    red, green, blue = _rgb(background)
    assert max(red, green, blue) - min(red, green, blue) > 40, (
        f"primary button background {background} is not saturated enough "
        f"to be a Bulma primary — did Bulma CSS actually load?"
    )

    page.screenshot(path=str(SCREENSHOT_DIR / "homepage.png"), full_page=True)


def test_modifier_classes_render_distinct_colours(
    live_server, page, collected_static  # noqa: ARG001
) -> None:
    """Distinct `is-*` modifiers must resolve to distinct backgrounds."""
    page.goto(live_server.url)

    def bg(test_id: str) -> tuple[int, int, int]:
        el = page.get_by_test_id(test_id)
        return _rgb(el.evaluate("el => getComputedStyle(el).backgroundColor"))

    primary, link, danger = bg("primary-button"), bg("link-button"), bg("danger-button")
    assert len({primary, link, danger}) == 3, (
        f"`is-primary` ({primary}), `is-link` ({link}), and `is-danger` ({danger}) "
        f"do not all render distinct backgrounds — modifier cascade is broken"
    )


def test_calendar_extension_css_is_served(
    live_server, page, collected_static  # noqa: ARG001
) -> None:
    """An element carrying a calendar-extension class must pick up its rules.

    tests/settings.py enables bulma-calendar. We inject a .datetimepicker
    into the DOM and assert that the extension's `display: none` rule
    applies — a div's default is `display: block`, so this only flips if
    the calendar CSS was actually concatenated into bulma.css.
    """
    page.goto(live_server.url)
    display = page.evaluate(
        """() => {
            const el = document.createElement('div');
            el.className = 'datetimepicker';
            document.body.appendChild(el);
            const value = getComputedStyle(el).display;
            el.remove();
            return value;
        }"""
    )
    assert display == "none", (
        f"datetimepicker resolved to `display: {display}` — expected `none` "
        f"from bulma-calendar's base rule. Calendar extension CSS is not applied."
    )
