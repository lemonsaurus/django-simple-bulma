"""
Custom finders that can be used together
with StaticFileStorage objects to find
files that should be collected by collectstatic.
"""
from pathlib import Path

import sass
from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage


class SimpleBulmaFinder(BaseFinder):
    """
    A custom Finder class to compile bulma to static files,
    and then return paths to those static files so they may be collected
    by the static collector.
    """

    def __init__(self):
        """Initialize the finder with user settings and paths."""
        # Try to get the Bulma settings. The user may not have created this dict.
        try:
            self.bulma_settings = settings.BULMA_SETTINGS
        except AttributeError:
            self.bulma_settings = {}

        self.simple_bulma_path = Path(__file__).resolve().parent
        self.extensions = self.bulma_settings.get("extensions", "_all")
        self.variables = self.bulma_settings.get("variables", {})
        self.storage = FileSystemStorage(self.simple_bulma_path)

    def _get_bulma_css(self):
        """Compiles the bulma css file and returns its relative path."""
        # Start by unpacking the users custom variables
        scss_string = ""
        for var, value in self.variables.items():
            scss_string += f"${var}: {value};\n"

        # Now load bulma
        scss_string += f'@import "{self.simple_bulma_path}/bulma.sass";'

        # Now load in the extensions that the user wants
        if self.extensions == "_all":
            scss_string += f'@import "{self.simple_bulma_path}/sass/extensions/_all";\n'
        elif isinstance(self.extensions, list):
            for extension in self.extensions:
                scss_string += f'@import "{self.simple_bulma_path}/sass/extensions/_{extension}";\n'

        # Store this as a css file
        css_string = sass.compile(string=scss_string)
        with open(f"{self.simple_bulma_path}/css/bulma.css", "w") as bulma_css:
            bulma_css.write(css_string)

        return "css/bulma.css"

    def _get_bulma_js(self):
        """
        Return a list of all the js files that are
        needed for the users selected extensions.
        """
        js_files = []
        js_folder = self.simple_bulma_path / "js"

        if self.extensions == "_all":
            for filename in js_folder.iterdir():
                js_files.append(f"js/{filename.name}")
        else:
            for filename in js_folder.iterdir():
                extension_name = str(filename.stem)

                if extension_name in self.extensions:
                    js_files.append(f"js/{filename.name}")

        return js_files

    def find(self, path, all=False):
        """
        Given a relative file path, find an absolute file path.

        If the ``all`` parameter is False (default) return only the first found
        file path; if True, return a list of all found files paths.
        """
        absolute_path = str(self.simple_bulma_path / path)

        if all:
            return [absolute_path]
        return absolute_path

    def list(self, ignore_patterns):
        """
        Return a two item iterable consisting of
        the relative path and storage instance.
        """
        files = [self._get_bulma_css()]
        files.extend(self._get_bulma_js())

        for path in files:
            yield path, self.storage
