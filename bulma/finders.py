"""
Custom finders that can be used together
with StaticFileStorage objects to find
files that should be collected by collectstatic.
"""

from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage


class SimpleBulmaFinder(BaseFinder):
    """
    A custom Finder class to compile bulma to static files,
    and then return paths to those static files so they may be collected
    by the static collector.
    """

    storage_class = FileSystemStorage

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
        raise NotImplementedError("subclasses of BaseFinder must provide a list() method")
