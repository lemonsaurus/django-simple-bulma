"""
Custom finders that can be used together
with StaticFileStorage objects to find
files that should be collected by collectstatic.
"""

from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import sass


class SimpleBulmaFinder(BaseFinder):
    """
    A custom Finder class to compile bulma to static files,
    and then return paths to those static files so they may be collected
    by the static collector.
    """

    storage_class = FileSystemStorage

    def _get_bulma_css(self):
        """
        Build and compile the bulma css file.
        """

        # Start by unpacking the users custom variables
        bulma_settings = settings.BULMA_SETTINGS
        scss_string = ""
        for var, value in bulma_settings.get("variables", []):
            scss_string += f"${var}: {value}\n"

        # Now load in the extensions that the user wants
        extensions = bulma_settings.get("extensions", True)

        if extensions is True:
            scss_string += '@import "sass/extensions/_all"'
        elif isinstance(extensions, list):
            for extension in extensions:
                scss_string += f'@import "sass/extensions/{extension}"'

        # Finally, load bulma
        scss_string += '@import "bulma"'

        # Store this as a css file
        css_string = sass.compile(string=scss_string)
        # Save to file

        return  # The file

    def _get_bulma_js(self):
        """
        Returns a list of all the js files that are
        needed for the users selected extensions.
        """

        pass

    def find(self, path, all=False):
        """
        Given a relative file path, find an absolute file path.

        If the ``all`` parameter is False (default) return only the first found
        file path; if True, return a list of all found files paths.
        """

        raise NotImplementedError("subclasses of BaseFinder must provide a find() method")

    def list(self, ignore_patterns):
        """
        Given an optional list of paths to ignore, return a two item iterable
        consisting of the relative path and storage instance.
        """

        pass
