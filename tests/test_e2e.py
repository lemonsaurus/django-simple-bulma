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

from pathlib import Path

import pytest
from django.core.management import call_command

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
    SCREENSHOT_DIR.mkdir(exist_ok=True)


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


def test_primary_and_danger_render_different_colours(
    live_server, page, collected_static  # noqa: ARG001
) -> None:
    """Distinct `is-*` modifiers must resolve to distinct backgrounds."""
    page.goto(live_server.url)

    def bg(test_id: str) -> tuple[int, int, int]:
        el = page.get_by_test_id(test_id)
        return _rgb(el.evaluate("el => getComputedStyle(el).backgroundColor"))

    primary, danger = bg("primary-button"), bg("danger-button")
    assert primary != danger, (
        "`.button.is-primary` and `.button.is-danger` render identically — "
        "Bulma modifier classes are not taking effect"
    )


def test_calendar_extension_css_is_served(
    live_server, page, collected_static  # noqa: ARG001
) -> None:
    """An element carrying a calendar-extension class must pick up its rules.

    tests/settings.py enables bulma-calendar. We inject a .datetimepicker
    into the DOM and check that its layout was affected. If the extension
    CSS was not concatenated into bulma.css, the element has no styling
    and its dimensions stay at the browser default.
    """
    page.goto(live_server.url)
    width = page.evaluate(
        """() => {
            const el = document.createElement('div');
            el.className = 'datetimepicker';
            el.style.display = 'block';
            document.body.appendChild(el);
            const w = el.getBoundingClientRect().width;
            el.remove();
            return w;
        }"""
    )
    assert width > 0, "datetimepicker has zero width — calendar CSS is not applied"
