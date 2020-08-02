"""
Custom collectstatic finders.

These finders that can be used together with StaticFileStorage
objects to find files that should be collected by collectstatic.
"""
from os.path import abspath
from pathlib import Path
from typing import List, Tuple, Union

import sass
from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage


class SimpleBulmaFinder(BaseFinder):
    """
    Custom Finder to compile Bulma static files.

    Returns paths to those static files so they may be collected
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
        self.bulma_submodule_path = self.simple_bulma_path / 'bulma' / 'sass'
        self.custom_scss = self.bulma_settings.get("custom_scss", [])
        self.extensions = self.bulma_settings.get("extensions", "_all")
        self.variables = self.bulma_settings.get("variables", {})
        self.output_style = self.bulma_settings.get("output_style", 'nested')
        self.storage = FileSystemStorage(self.simple_bulma_path)

    def _get_bulma_css(self) -> str:
        """Compiles the bulma css file and returns its relative path."""
        # Start by unpacking the users custom variables
        scss_string = '@charset "utf-8";\n'
        for var, value in self.variables.items():
            scss_string += f"${var}: {value};\n"

        # SASS wants paths with forward slash:
        sass_bulma_path = str(self.simple_bulma_path).replace('\\', '/')
        sass_bulma_submodule_path = str(self.bulma_submodule_path).replace('\\', '/')

        scss_string += f'@import "{sass_bulma_submodule_path}/utilities/_all";\n'

        # Now load bulma dynamically.
        # Doing this instead of just referencing bulma.sass is preperation for issue #6
        for dirname in self.bulma_submodule_path.iterdir():

            # We already added this earlier
            if dirname.name == "utilities":
                continue

            scss_string += f'@import "{sass_bulma_submodule_path}/{dirname.name}/_all";\n'

        # Now load in the extensions that the user wants
        if self.extensions == "_all":
            scss_string += f'@import "{sass_bulma_path}/extensions/_all";\n'
        elif isinstance(self.extensions, list):
            for extension in self.extensions:

                # Check if the extension exists
                extensions_folder = self.simple_bulma_path / "extensions"
                extensions = [extension.stem[1:] for extension in extensions_folder.iterdir()]
                if extension in extensions:
                    scss_string += f'@import "{sass_bulma_path}/extensions/_{extension}";\n'

        # Store this as a css file
        if hasattr(sass, "libsass_version"):
            css_string = sass.compile(string=scss_string, output_style=self.output_style)
        else:
            # If the user has the sass module installed in addition to libsass,
            # warn the user and fail hard.
            raise UserWarning(
                "There was an error compiling your Bulma CSS. This error is "
                "probably caused by having the `sass` module installed, as the two modules "
                "are in conflict, causing django-simple-bulma to import the wrong sass namespace."
                "\n"
                "Please ensure you have only the `libsass` module installed, "
                "not both `sass` and `libsass`, or this application will not work."
            )

        css_path = self.simple_bulma_path / "css" / "bulma.css"
        with open(css_path, "w") as bulma_css:
            bulma_css.write(css_string)

        return "css/bulma.css"

    def _get_custom_css(self) -> str:
        """Compiles any custom-specified SASS and returns its relative path."""
        paths = []

        for scss_path in self.custom_scss:
            # Check that we can process this
            relative_path = self.find_relative_staticfiles(scss_path)

            if relative_path is None:
                if "static/" in scss_path:
                    relative_path = Path(scss_path.split("static/", 1)[-1])
                else:
                    raise ValueError(
                        "We couldn't figure out where the static directory for the given SCSS "
                        f"path is: \"{scss_path}\". If the given path doesn't contain "
                        "\"static/\", then you may need to add it to your STATICFILES_DIRS "
                        "setting."
                    )

            # SASS wants paths with forward slash:
            scss_path = str(scss_path).replace('\\', '/')

            # Now load up the scss file
            scss_string = f'@import "{scss_path}";'

            # Store this as a css file - we don't check and raise here because it would have
            # already happened earlier, during the Bulma compilation
            css_string = sass.compile(string=scss_string, output_style=self.output_style)

            css_path = self.simple_bulma_path / relative_path.parent
            css_path.mkdir(exist_ok=True)
            css_path = f"{css_path}/{relative_path.stem}.css"

            with open(css_path, "w") as css_file:
                css_file.write(css_string)

            paths.append(f"{relative_path.parent}/{relative_path.stem}.css")

        return paths

    def _get_bulma_js(self) -> List[str]:
        """Return a list of all the js files that are needed for the users selected extensions."""
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

    @staticmethod
    def find_relative_staticfiles(path: Union[str, Path]) -> Union[Path, None]:
        """
        Returns a given path, relative to one of the paths in STATICFILES_DIRS.

        Returns None if the given path isn't available within STATICFILES_DIRS.
        """
        if not isinstance(path, Path):
            path = Path(abspath(path))

        for directory in settings.STATICFILES_DIRS:
            directory = Path(abspath(directory))

            if directory in path.parents:
                return path.relative_to(directory)

    def find(self, path: str, all: bool = False) -> Union[List[str], str]:
        """
        Given a relative file path, find an absolute file path.

        If the ``all`` parameter is False (default) return only the first found
        file path; if True, return a list of all found files paths.
        """
        absolute_path = str(self.simple_bulma_path / path)

        if all:
            return [absolute_path]
        return absolute_path

    def list(self, _: List[str]) -> Tuple[str, FileSystemStorage]:
        """Return a two item iterable consisting of the relative path and storage instance."""
        files = [self._get_bulma_css()]
        files.extend(self._get_custom_css())
        files.extend(self._get_bulma_js())

        for path in files:
            yield path, self.storage
