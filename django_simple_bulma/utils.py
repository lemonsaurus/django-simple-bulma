"""Django Simple Bulma utilities. Ultimately helps ensure DRY code."""

import logging
import re
from pathlib import Path
from typing import Generator, List, Union

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Captures any word characters before "_variables"
# Basically equivalent to "\w+_variables"
variables_name_re = re.compile(r"^(?P<name>\w+)_variables$")
themes = []

# If BULMA_SETTINGS has not been declared if no extensions
# have been defined, default to all extensions.
try:
    if hasattr(settings, "BULMA_SETTINGS"):
        extensions = settings.BULMA_SETTINGS.get("extensions", [])
        fontawesome_token = settings.BULMA_SETTINGS.get("fontawesome_token", "")
        for key in settings.BULMA_SETTINGS:
            match = variables_name_re.match(key)
            if match:
                themes.append(match.group("name"))
    else:
        extensions = []
        fontawesome_token = ""
except (ImproperlyConfigured, AttributeError):
    # Django settings not configured yet (e.g., during testing)
    extensions = []
    fontawesome_token = ""

simple_bulma_path = Path(__file__).resolve().parent


def get_themes() -> list:
    """Get the list of available themes dynamically."""
    themes = []
    try:
        if hasattr(settings, "BULMA_SETTINGS"):
            for key in settings.BULMA_SETTINGS:
                match = variables_name_re.match(key)
                if match:
                    themes.append(match.group("name"))
    except (ImproperlyConfigured, AttributeError):
        pass
    return themes


# (Path, str) pairs describing a relative path in an extension and a glob pattern to search for
sass_files_searches = (
    (Path("src/sass"), "_all.sass"),
    (Path("src/sass"), "index.sass"),
    (Path("src/sass"), "*.sass"),
    (Path("src"), "*.s[ac]ss"),
    (Path("dist"), "*.sass"),
    (Path("dist"), "*.min.css"),
    (Path("dist"), "*.css"),
    (Path(""), "*.s[ac]ss"),
)

logger = logging.getLogger("django-simple-bulma")


def is_enabled(extension: Union[Path, str]) -> bool:
    """Return whether an extension is enabled or not."""
    # Get extensions dynamically to support override_settings in tests
    try:
        if hasattr(settings, "BULMA_SETTINGS"):
            current_extensions = settings.BULMA_SETTINGS.get("extensions", [])
        else:
            current_extensions = []
    except (ImproperlyConfigured, AttributeError):
        current_extensions = []

    if isinstance(extension, Path):
        return current_extensions == "all" or extension.name in current_extensions
    return current_extensions == "all" or extension in current_extensions


def get_js_files() -> Generator[str, None, None]:
    """Yield all the js files that are needed for the users selected extensions."""
    # For every extension...
    extensions = []
    for ext in (simple_bulma_path / "extensions").iterdir():
        # ...check if it is enabled...
        if is_enabled(ext):
            dist_folder = ext / "dist"

            # ...and add its JS file.
            # This really makes a lot of assumptions about the extension,
            # but so does everything else up until here.
            # Basically, try get a minified version first before settling
            # for whatever might be there.
            js_file = next(dist_folder.rglob("*.min.js"), None) or \
                next(dist_folder.rglob("*.js"), None)
            if js_file:
                yield js_file.relative_to(simple_bulma_path).as_posix()

            # Add the name of the extension to the list of enabled extensions
            extensions.append(ext.name)

    # If we've got only bulma-collapsible, we need the runner, too.
    if "bulma-collapsible" in extensions and "bulma-collapsible-runner" not in extensions:
        runner_js = (
            simple_bulma_path
            / "extensions/bulma-collapsible-runner/dist/js/bulma-collapsible-runner.js"
        )
        yield runner_js.relative_to(simple_bulma_path).as_posix()


def get_sass_files(ext: Path) -> List[Path]:
    """Given the path to an extension, find and yield all files that should be imported."""
    for rel_path, glob in sass_files_searches:
        src_files = list((ext / rel_path).rglob(glob))

        for i, src in enumerate(src_files):
            # Remove suffix from css files, otherwise they wont get compiled, only referenced
            if glob.endswith(".css"):
                src = src.with_suffix("")
            src_files[i] = src.relative_to(simple_bulma_path)

        if src_files:
            return src_files

    # Extension has no stylesheets
    return []
