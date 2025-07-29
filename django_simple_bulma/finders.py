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
from django.contrib.staticfiles.finders import BaseFinder, get_finder
from django.core.files.storage import FileSystemStorage

from .css_variables import convert_sass_variables_to_css
from .utils import (
    get_js_files,
    get_sass_files,
    get_themes,
    is_enabled,
    simple_bulma_path,
)


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

        self.bulma_submodule_path = simple_bulma_path / "bulma" / "sass"
        self.custom_scss = self.bulma_settings.get("custom_scss", [])
        self.variables = self.bulma_settings.get("variables", {})
        self.output_style = self.bulma_settings.get("output_style", "nested")
        self.storage = FileSystemStorage(simple_bulma_path)

        # Make a list of all the finders except this one.
        # We use this in the custom SCSS handler.
        other_finders = settings.STATICFILES_FINDERS.copy()
        other_finders.remove("django_simple_bulma.finders.SimpleBulmaFinder")
        self.other_finders = [get_finder(finder) for finder in other_finders]

    @staticmethod
    def _get_extension_imports() -> str:
        """Return a string that, in SASS, imports all enabled extensions."""
        scss_imports = ""

        # Load extensions in alphabetical order (deterministic and no interdependencies)
        for ext in sorted((simple_bulma_path / "extensions").iterdir()):

            if is_enabled(ext):
                for src in get_sass_files(ext):
                    scss_imports += f"@import '{src.as_posix()}';\n"

        return scss_imports

    @staticmethod
    def _unpack_variables(variables: dict) -> str:
        """Unpacks SASS variables from a dictionary to a compilable string."""
        scss_string = ""
        for var, value in variables.items():
            scss_string += f"${var}: {value};\n"
        return scss_string

    @staticmethod
    def _get_bulma_js() -> List[str]:
        """Return a list of all the js files that are needed for the users selected extensions."""
        return list(get_js_files())

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

    def _get_bulma_css(self) -> List[str]:
        """
        Gets or compiles the bulma css files for each theme and returns their relative paths.

        For Bulma 1.0+, uses pre-compiled CSS with CSS variable injection for customization.
        This provides better performance and backwards compatibility with existing themes.
        """
        # Get current configuration
        current_extensions = (
            settings.BULMA_SETTINGS.get("extensions", [])
            if hasattr(settings, "BULMA_SETTINGS") else []
        )
        has_extensions = bool(current_extensions)
        themes = get_themes()

        # Check Bulma version
        version_file = self.bulma_submodule_path.parent / "package.json"
        is_bulma_1_plus = False
        if version_file.exists():
            import json
            with open(version_file, "r", encoding="utf-8") as f:
                package_data = json.load(f)
                version = package_data.get("version", "0.0.0")
                is_bulma_1_plus = version.startswith("1.")

        # For Bulma 1.0+, use pre-compiled CSS with CSS variable customization
        if is_bulma_1_plus:
            return self._get_bulma_1_css(themes, has_extensions)

        # For older Bulma versions, fall back to SASS compilation
        return self._compile_sass_fallback()

    def _get_bulma_1_css(self, themes: List[str], has_extensions: bool) -> List[str]:
        """
        Generate CSS files for Bulma 1.0+ using pre-compiled CSS with CSS variable injection.

        Args:
            themes: List of theme names (e.g., ['dark', 'light'])
            has_extensions: Whether extensions are enabled

        Returns:
            List of relative paths to generated CSS files
        """
        theme_paths = []
        bulma_root = self.bulma_submodule_path.parent
        precompiled_css = bulma_root / "css" / "bulma.min.css"

        if not precompiled_css.exists():
            raise FileNotFoundError(
                f"Pre-compiled Bulma CSS not found at {precompiled_css}. "
                f"This file should be available in the Bulma 1.0+ distribution at "
                f"css/bulma.min.css. Please ensure the Bulma submodule is updated "
                f"to version 1.0+ and contains the pre-compiled CSS files."
            )

        # Read the base pre-compiled CSS
        with open(precompiled_css, "r", encoding="utf-8") as f:
            base_css = f.read()

        # Process default theme first (empty string means default)
        theme_names = [""] + themes

        for theme in theme_names:
            # Get variables for this theme
            variables = self.variables.copy()  # Default variables
            if theme:
                # Override with theme-specific variables
                theme_key = f"{theme}_variables"
                if hasattr(settings, "BULMA_SETTINGS") and theme_key in settings.BULMA_SETTINGS:
                    variables.update(settings.BULMA_SETTINGS[theme_key])

            # Generate CSS variable overrides
            css_variables = convert_sass_variables_to_css(variables)

            # Collect extension CSS
            extension_css = ""
            if has_extensions:
                extension_css = self._get_extension_css()

            # Combine all CSS
            final_css = base_css
            if css_variables:
                final_css = css_variables + "\n" + final_css
            if extension_css:
                final_css = final_css + "\n" + extension_css

            # Write theme CSS file
            theme_filename = f"{theme + '_' if theme else ''}bulma.css"
            theme_path = f"css/{theme_filename}"
            css_path = simple_bulma_path / theme_path
            css_path.parent.mkdir(parents=True, exist_ok=True)

            with open(css_path, "w", encoding="utf-8") as f:
                f.write(final_css)

            theme_paths.append(theme_path)

        return theme_paths

    def _get_extension_css(self) -> str:
        """
        Collect CSS from enabled extensions.

        Returns:
            Combined CSS from all enabled extensions
        """
        extension_css_parts = []

        # Process extensions in alphabetical order for deterministic CSS generation
        for ext_dir in sorted((simple_bulma_path / "extensions").iterdir()):
            if is_enabled(ext_dir):
                # Look for CSS files in the extension
                dist_dir = ext_dir / "dist"
                if dist_dir.exists():
                    for css_file in dist_dir.glob("*.css"):
                        if not css_file.name.endswith(".min.css"):  # Prefer non-minified
                            try:
                                with open(css_file, "r", encoding="utf-8") as f:
                                    extension_css_parts.append(f"/* Extension: {ext_dir.name} */")
                                    extension_css_parts.append(f.read())
                            except (IOError, UnicodeDecodeError):
                                # Skip files that can't be read
                                continue

        return "\n".join(extension_css_parts)

    def _compile_sass_fallback(self) -> List[str]:
        """Legacy SASS compilation method (for Bulma < 1.0 compatibility)."""
        # Check for proper libsass installation
        if not hasattr(sass, "libsass_version"):
            raise UserWarning(
                "There was an error compiling your Bulma CSS. This error is "
                "probably caused by having the `sass` module installed, as the two modules "
                "are in conflict, causing django-simple-bulma to import the wrong sass namespace."
                "\n"
                "Please ensure you have only the `libsass` module installed, "
                "not both `sass` and `libsass`, or this application will not work."
            )

        # SASS wants paths with forward slash:
        sass_bulma_submodule_path = self.bulma_submodule_path \
            .relative_to(simple_bulma_path).as_posix()

        bulma_string = f"@import '{sass_bulma_submodule_path}/utilities/_index';\n"

        # Load Bulma modules in the official order (from bulma/sass/_index.scss)
        # Note: utilities is already loaded above
        bulma_module_order = [
            "themes", "base", "elements", "form", "components",
            "grid", "layout", "helpers"
        ]

        for module_name in bulma_module_order:
            module_path = self.bulma_submodule_path / module_name
            if module_path.exists():
                bulma_string += f"@import '{sass_bulma_submodule_path}/{module_name}/_index';\n"

        # Handle base/skeleton separately as it's loaded after layout in the official order
        skeleton_path = self.bulma_submodule_path / "base" / "skeleton.sass"
        if skeleton_path.exists():
            bulma_string += f"@import '{sass_bulma_submodule_path}/base/skeleton';\n"

        # Now load in the extensions that the user wants
        extensions_string = self._get_extension_imports()

        # Generate SASS strings for each theme
        # The default theme is treated as ""
        theme_paths = []
        themes = get_themes()
        for theme in [""] + themes:
            scss_string = "@charset 'utf-8';\n"

            # Unpack this theme's custom variables
            variables = self.variables
            if theme:
                variables = settings.BULMA_SETTINGS[f"{theme}_variables"]
            scss_string += self._unpack_variables(variables)

            scss_string += bulma_string
            scss_string += extensions_string

            # Store this as a css file
            css_string = sass.compile(string=scss_string,
                                      output_style=self.output_style,
                                      include_paths=[simple_bulma_path.as_posix()])

            theme_path = f"css/{theme + '_' if theme else ''}bulma.css"
            css_path = simple_bulma_path / theme_path
            with open(css_path, "w", encoding="utf-8") as bulma_css:
                bulma_css.write(css_string)
            theme_paths.append(theme_path)

        return theme_paths

    def _get_custom_css(self) -> str:
        """Compiles any custom-specified SASS and returns its relative path."""
        paths = []

        for scss_path in self.custom_scss:
            # Simplify the path to be only the relative path, if they've included the whole thing.
            relative_path = scss_path.split("static/", 1)[-1]

            # Check that we can find this file with one of the other finders.
            absolute_path = None
            for finder in self.other_finders:
                found_path = finder.find(relative_path)
                if found_path and found_path != []:  # Ensure it's not empty list
                    absolute_path = found_path
                    break

            # Raise an error if we can't find it.
            if not absolute_path:
                raise ValueError(
                    f"Unable to locate the SCSS file \"{scss_path}\". Make sure the file exists, "
                    "and ensure that one of the other configured Finders are able to locate it. \n"
                    "See https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/ for more "
                    "information about how static files are discovered."
                )

            # Prepare the paths. SASS wants forwardslash string, the rest needs a Path.
            absolute_path = str(absolute_path).replace("\\", "/")
            relative_path = Path(relative_path)

            # Now load up the scss file
            scss_string = f'@import "{absolute_path}";'

            # Store this as a css file - we don't check and raise here because it would have
            # already happened earlier, during the Bulma compilation
            css_string = sass.compile(string=scss_string, output_style=self.output_style)

            css_path = simple_bulma_path / relative_path.parent
            css_path.mkdir(parents=True, exist_ok=True)
            css_path = f"{css_path}/{relative_path.stem}.css"

            with open(css_path, "w") as css_file:
                css_file.write(css_string)

            paths.append(f"{relative_path.parent}/{relative_path.stem}.css")

        return paths

    def find(self, path: str, find_all: bool = False, all: bool = False) -> Union[List[str], str]:
        """
        Given a relative file path, find an absolute file path.

        Django 5.2 uses the ``find_all` instead of the ``all`` keyword argument.

        If the ``find_all`` or ``all`` parameter is False (default) return only
        the first found file path; if True, return a list of all found files
        paths.
        """
        absolute_path = str(simple_bulma_path / path)

        if find_all or all:
            return [absolute_path]
        return absolute_path

    def list(self, _: List[str]) -> Tuple[str, FileSystemStorage]:
        """Return a two item iterable consisting of the relative path and storage instance."""
        files = self._get_bulma_css()
        files.extend(self._get_custom_css())
        files.extend(self._get_bulma_js())

        for path in files:
            yield path, self.storage
