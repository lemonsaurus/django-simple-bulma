"""Tests for django_simple_bulma utility functions."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import override_settings
from django_simple_bulma.utils import (
    get_js_files,
    get_sass_files,
    is_enabled,
    simple_bulma_path,
)


class TestIsEnabled:
    """Test the is_enabled utility function."""

    @override_settings(BULMA_SETTINGS={'extensions': ['bulma-tooltip', 'bulma-calendar']})
    def test_is_enabled_with_specific_extensions(self) -> None:
        """Test is_enabled with specific extensions list."""
        assert is_enabled('bulma-tooltip') is True
        assert is_enabled('bulma-calendar') is True
        assert is_enabled('bulma-slider') is False

    @override_settings(BULMA_SETTINGS={'extensions': 'all'})
    def test_is_enabled_with_all_extensions(self) -> None:
        """Test is_enabled when extensions is 'all'."""
        assert is_enabled('any-extension') is True
        assert is_enabled('bulma-tooltip') is True

    @override_settings(BULMA_SETTINGS={'extensions': []})
    def test_is_enabled_with_empty_extensions(self) -> None:
        """Test is_enabled with empty extensions list."""
        assert is_enabled('bulma-tooltip') is False
        assert is_enabled('any-extension') is False

    def test_is_enabled_with_path_object(self) -> None:
        """Test is_enabled with Path objects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ext_path = Path(temp_dir) / 'bulma-tooltip'
            ext_path.mkdir()

            with override_settings(BULMA_SETTINGS={'extensions': ['bulma-tooltip']}):
                assert is_enabled(ext_path) is True

            with override_settings(BULMA_SETTINGS={'extensions': ['bulma-calendar']}):
                assert is_enabled(ext_path) is False


class TestGetJsFiles:
    """Test the get_js_files utility function."""

    @patch('django_simple_bulma.utils.is_enabled')
    def test_get_js_files_finds_minified_first(self, mock_is_enabled: patch) -> None:
        """Test get_js_files prefers minified JS files."""
        mock_is_enabled.return_value = True

        # Create mock extension directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create extension with both minified and regular JS
            ext_dir = temp_path / 'extensions' / 'bulma-tooltip'
            dist_dir = ext_dir / 'dist'
            dist_dir.mkdir(parents=True)

            (dist_dir / 'bulma-tooltip.js').touch()
            (dist_dir / 'bulma-tooltip.min.js').touch()

            # Mock simple_bulma_path to point to our temp directory
            with patch('django_simple_bulma.utils.simple_bulma_path', temp_path):
                js_files = list(get_js_files())

            # Should prefer .min.js file
            assert any('min.js' in js_file for js_file in js_files)

    @patch('django_simple_bulma.utils.is_enabled')
    def test_get_js_files_collapsible_runner(self, mock_is_enabled: patch) -> None:
        """Test get_js_files adds collapsible runner when needed."""
        # Mock is_enabled to return True only for bulma-collapsible
        def mock_enabled(ext: str) -> bool:
            if hasattr(ext, 'name'):
                return ext.name == 'bulma-collapsible'
            return ext == 'bulma-collapsible'
        mock_is_enabled.side_effect = mock_enabled

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create bulma-collapsible extension
            ext_dir = temp_path / 'extensions' / 'bulma-collapsible'
            dist_dir = ext_dir / 'dist'
            dist_dir.mkdir(parents=True)
            (dist_dir / 'bulma-collapsible.min.js').touch()

            # Create bulma-collapsible-runner extension
            runner_ext_dir = temp_path / 'extensions' / 'bulma-collapsible-runner'
            runner_dist_dir = runner_ext_dir / 'dist' / 'js'
            runner_dist_dir.mkdir(parents=True)
            (runner_dist_dir / 'bulma-collapsible-runner.js').touch()

            with patch('django_simple_bulma.utils.simple_bulma_path', temp_path):
                js_files = list(get_js_files())

            # Should include the collapsible runner
            assert any(
                'collapsible-runner' in str(js_file) for js_file in js_files
            )

    @patch('django_simple_bulma.utils.simple_bulma_path')
    @patch('django_simple_bulma.utils.is_enabled')
    def test_get_js_files_no_enabled_extensions(
        self, mock_is_enabled: patch, mock_path: patch
    ) -> None:
        """Test get_js_files with no enabled extensions."""
        mock_is_enabled.return_value = False
        mock_path.__truediv__.return_value.iterdir.return_value = []

        js_files = list(get_js_files())
        assert js_files == []


class TestGetSassFiles:
    """Test the get_sass_files utility function."""

    def test_get_sass_files_prioritizes_all_sass(self) -> None:
        """Test get_sass_files finds _all.sass first."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ext_path = Path(temp_dir)

            # Create src/sass directory with _all.sass
            sass_dir = ext_path / 'src' / 'sass'
            sass_dir.mkdir(parents=True)
            (sass_dir / '_all.sass').touch()
            (sass_dir / 'other.sass').touch()

            with patch('django_simple_bulma.utils.simple_bulma_path', ext_path):
                sass_files = get_sass_files(ext_path)

            assert len(sass_files) == 1
            assert sass_files[0].name == '_all.sass'

    def test_get_sass_files_falls_back_to_index(self) -> None:
        """Test get_sass_files falls back to index.sass."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ext_path = Path(temp_dir)

            # Create src/sass directory with index.sass
            sass_dir = ext_path / 'src' / 'sass'
            sass_dir.mkdir(parents=True)
            (sass_dir / 'index.sass').touch()

            with patch('django_simple_bulma.utils.simple_bulma_path', ext_path):
                sass_files = get_sass_files(ext_path)

            assert len(sass_files) == 1
            assert sass_files[0].name == 'index.sass'

    def test_get_sass_files_handles_css_files(self) -> None:
        """Test get_sass_files processes CSS files correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ext_path = Path(temp_dir)

            # Create dist directory with CSS file
            dist_dir = ext_path / 'dist'
            dist_dir.mkdir(parents=True)
            (dist_dir / 'style.css').touch()

            with patch('django_simple_bulma.utils.simple_bulma_path', ext_path):
                sass_files = get_sass_files(ext_path)

            assert len(sass_files) == 1
            # CSS files should have suffix removed for compilation
            assert sass_files[0].suffix == ''

    def test_get_sass_files_no_stylesheets(self) -> None:
        """Test get_sass_files returns empty list when no stylesheets found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ext_path = Path(temp_dir)

            with patch('django_simple_bulma.utils.simple_bulma_path', ext_path):
                sass_files = get_sass_files(ext_path)

            assert sass_files == []


class TestSettingsLoading:
    """Test settings loading and theme detection."""

    @override_settings(BULMA_SETTINGS={
        'extensions': ['bulma-tooltip'],
        'fontawesome_token': 'test123',
        'alt_variables': {'primary': '#fff'},
        'dark_variables': {'primary': '#000'},
    })
    def test_settings_loaded_correctly(self) -> None:
        """Test that settings are loaded and themes detected."""
        # Need to reload the module to pick up new settings
        import importlib
        from django_simple_bulma import utils
        importlib.reload(utils)

        assert 'bulma-tooltip' in utils.extensions
        assert utils.fontawesome_token == 'test123'
        assert 'alt' in utils.themes
        assert 'dark' in utils.themes

    def test_no_bulma_settings(self) -> None:
        """Test behavior when BULMA_SETTINGS is not defined."""
        with override_settings(BULMA_SETTINGS=None):

            # Reload utils to pick up the change
            import importlib
            from django_simple_bulma import utils
            importlib.reload(utils)

            assert utils.extensions == []
            assert utils.fontawesome_token == ""
            assert utils.themes == []

    @override_settings(BULMA_SETTINGS={'test_variables': {'color': 'blue'}})
    def test_theme_detection_regex(self) -> None:
        """Test theme detection using regex pattern."""
        import importlib
        from django_simple_bulma import utils
        importlib.reload(utils)

        assert 'test' in utils.themes


class TestModuleConstants:
    """Test module-level constants and paths."""

    def test_simple_bulma_path_exists(self) -> None:
        """Test that simple_bulma_path points to valid directory."""
        assert simple_bulma_path.exists()
        assert simple_bulma_path.is_dir()
        assert (simple_bulma_path / '__init__.py').exists()

    def test_sass_files_searches_structure(self) -> None:
        """Test sass_files_searches has expected structure."""
        from django_simple_bulma.utils import sass_files_searches

        assert len(sass_files_searches) > 0
        for search in sass_files_searches:
            assert len(search) == 2
            assert isinstance(search[0], Path)
            assert isinstance(search[1], str)
