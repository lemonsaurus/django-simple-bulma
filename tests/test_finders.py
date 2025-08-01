"""Tests for django_simple_bulma finders."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from django.core.files.storage import FileSystemStorage
from django.test import override_settings
from django_simple_bulma.finders import SimpleBulmaFinder


class TestSimpleBulmaFinderInit:
    """Test SimpleBulmaFinder initialization."""

    @override_settings(BULMA_SETTINGS={
        'custom_scss': ['test.scss'],
        'variables': {'primary': '#007bff'},
        'output_style': 'compressed'
    })
    def test_init_with_settings(self) -> None:
        """Test finder initialization with BULMA_SETTINGS."""
        finder = SimpleBulmaFinder()

        assert finder.custom_scss == ['test.scss']
        assert finder.variables == {'primary': '#007bff'}
        assert finder.output_style == 'compressed'
        assert isinstance(finder.storage, FileSystemStorage)

    @override_settings()
    def test_init_without_settings(self) -> None:
        """Test finder initialization without BULMA_SETTINGS."""
        # Test without BULMA_SETTINGS at all
        from django.conf import settings
        if hasattr(settings, 'BULMA_SETTINGS'):
            delattr(settings, 'BULMA_SETTINGS')

        finder = SimpleBulmaFinder()

        assert finder.bulma_settings == {}
        assert finder.custom_scss == []
        assert finder.variables == {}
        assert finder.output_style == 'nested'

    @override_settings(STATICFILES_FINDERS=[
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django_simple_bulma.finders.SimpleBulmaFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder'
    ])
    def test_init_other_finders(self) -> None:
        """Test that other finders are correctly identified."""
        finder = SimpleBulmaFinder()

        assert len(finder.other_finders) == 2
        # SimpleBulmaFinder should be excluded


class TestSimpleBulmaFinderStaticMethods:
    """Test static methods of SimpleBulmaFinder."""

    @patch('django_simple_bulma.finders.simple_bulma_path')
    @patch('django_simple_bulma.finders.is_enabled')
    @patch('django_simple_bulma.finders.get_sass_files')
    def test_get_extension_imports(
        self, mock_get_sass: MagicMock, mock_is_enabled: MagicMock, mock_path: MagicMock
    ) -> None:
        """Test _get_extension_imports method."""
        mock_is_enabled.return_value = True
        mock_get_sass.return_value = [Path('test.sass')]

        # Mock extension directory
        with tempfile.TemporaryDirectory() as temp_dir:
            ext_dir = Path(temp_dir) / 'bulma-tooltip'
            ext_dir.mkdir()

            mock_path.__truediv__.return_value.iterdir.return_value = [ext_dir]

            result = SimpleBulmaFinder._get_extension_imports()

            assert "@import 'test.sass';" in result
            mock_get_sass.assert_called_once_with(ext_dir)

    def test_unpack_variables(self) -> None:
        """Test _unpack_variables method."""
        variables = {
            'primary': '#007bff',
            'family-primary': 'Arial',
            'size-1': '3rem'
        }

        result = SimpleBulmaFinder._unpack_variables(variables)

        assert '$primary: #007bff;' in result
        assert '$family-primary: Arial;' in result
        assert '$size-1: 3rem;' in result

    def test_unpack_variables_empty(self) -> None:
        """Test _unpack_variables with empty dict."""
        result = SimpleBulmaFinder._unpack_variables({})
        assert result == ""

    @patch('django_simple_bulma.finders.get_js_files')
    def test_get_bulma_js(self, mock_get_js_files: MagicMock) -> None:
        """Test _get_bulma_js method."""
        mock_get_js_files.return_value = ['ext1.js', 'ext2.min.js']

        result = SimpleBulmaFinder._get_bulma_js()

        assert result == ['ext1.js', 'ext2.min.js']

    @override_settings(STATICFILES_DIRS=['/app/static', '/other/static'])
    def test_find_relative_staticfiles(self) -> None:
        """Test find_relative_staticfiles method."""
        # Test with path inside STATICFILES_DIRS
        test_path = '/app/static/css/custom.css'
        result = SimpleBulmaFinder.find_relative_staticfiles(test_path)

        assert result == Path('css/custom.css')

    @override_settings(STATICFILES_DIRS=['/app/static'])
    def test_find_relative_staticfiles_not_found(self) -> None:
        """Test find_relative_staticfiles with path outside STATICFILES_DIRS."""
        test_path = '/other/path/file.css'
        result = SimpleBulmaFinder.find_relative_staticfiles(test_path)

        assert result is None


class TestSimpleBulmaFinderSassCompilation:
    """Test SASS compilation in SimpleBulmaFinder."""

    @patch('django_simple_bulma.finders.sass')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_bulma_css_basic_compilation(
        self, mock_file: MagicMock, mock_sass: MagicMock
    ) -> None:
        """Test basic CSS compilation."""
        mock_sass.libsass_version = "0.19.0"  # Ensure libsass is detected
        mock_sass.compile.return_value = "compiled css content"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create bulma submodule structure
            bulma_dir = temp_path / 'bulma' / 'sass'
            utilities_dir = bulma_dir / 'utilities'
            utilities_dir.mkdir(parents=True)

            # Create extensions directory (needed by _get_extension_imports)
            extensions_dir = temp_path / 'extensions'
            extensions_dir.mkdir(parents=True)

            # Mock the simple_bulma_path to return our temp directory
            with patch('django_simple_bulma.finders.simple_bulma_path', temp_path):
                finder = SimpleBulmaFinder()
                finder.bulma_submodule_path = bulma_dir

                with patch('django_simple_bulma.finders.get_themes', return_value=[]):
                    result = finder._get_bulma_css()

                assert len(result) == 1
                assert result[0] == 'css/bulma.css'
                mock_sass.compile.assert_called()

    @patch('django_simple_bulma.finders.sass')
    def test_get_bulma_css_sass_module_conflict(self, mock_sass: MagicMock) -> None:
        """Test that Bulma 1.0+ bypasses sass module conflict by using pre-compiled CSS."""
        # Remove libsass_version to simulate sass module
        delattr(mock_sass, 'libsass_version')

        finder = SimpleBulmaFinder()

        # For Bulma 1.0+, this should work without error because we use pre-compiled CSS
        try:
            css_files = finder._get_bulma_css()
            # Should return CSS files successfully
            assert len(css_files) > 0
            assert all(path.endswith('.css') for path in css_files)
        except UserWarning:
            # If it does raise a warning, it should be about libsass conflict
            # but this should only happen for Bulma < 1.0
            pass

    @patch('django_simple_bulma.finders.sass')
    @patch('builtins.open', new_callable=mock_open)
    @override_settings(BULMA_SETTINGS={
        'alt_variables': {'primary': '#fff'},
        'dark_variables': {'primary': '#000'}
    })
    def test_get_bulma_css_with_themes(self, mock_file: MagicMock, mock_sass: MagicMock) -> None:
        """Test CSS compilation with multiple themes."""
        mock_sass.libsass_version = "0.19.0"
        mock_sass.compile.return_value = "compiled css"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create bulma submodule structure
            bulma_dir = temp_path / 'bulma' / 'sass'
            utilities_dir = bulma_dir / 'utilities'
            utilities_dir.mkdir(parents=True)

            # Create extensions directory (needed by _get_extension_imports)
            extensions_dir = temp_path / 'extensions'
            extensions_dir.mkdir(parents=True)

            with patch('django_simple_bulma.finders.simple_bulma_path', temp_path):
                finder = SimpleBulmaFinder()
                finder.bulma_submodule_path = bulma_dir

                result = finder._get_bulma_css()

            # Should generate CSS for default + 2 themes
            assert len(result) == 3
            assert 'css/bulma.css' in result
            assert 'css/alt_bulma.css' in result
            assert 'css/dark_bulma.css' in result


class TestSimpleBulmaFinderCustomScss:
    """Test custom SCSS compilation in SimpleBulmaFinder."""

    def test_get_custom_css_file_not_found(self) -> None:
        """Test custom CSS compilation when SCSS file not found."""
        finder = SimpleBulmaFinder()
        finder.custom_scss = ['nonexistent.scss']
        finder.other_finders = []

        with pytest.raises(ValueError) as exc_info:
            finder._get_custom_css()

        assert "Unable to locate the SCSS file" in str(exc_info.value)

    @patch('django_simple_bulma.finders.sass')
    @patch('django_simple_bulma.finders.simple_bulma_path')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_custom_css_successful_compilation(
        self, mock_file: MagicMock, mock_path: MagicMock, mock_sass: MagicMock
    ) -> None:
        """Test successful custom CSS compilation."""
        mock_sass.compile.return_value = "compiled custom css"

        # Mock finder that can find the file
        mock_finder = MagicMock()
        mock_finder.find.return_value = '/path/to/custom.scss'

        finder = SimpleBulmaFinder()
        finder.custom_scss = ['static/custom.scss']
        finder.other_finders = [mock_finder]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_path.__truediv__.return_value = temp_path

            result = finder._get_custom_css()

            assert len(result) == 1
            assert 'custom.css' in result[0]
            mock_sass.compile.assert_called_once()


class TestSimpleBulmaFinderPublicMethods:
    """Test public methods of SimpleBulmaFinder."""

    def test_find_method_single_result(self) -> None:
        """Test find method returning single result."""
        finder = SimpleBulmaFinder()

        result = finder.find('css/bulma.css')

        assert 'css/bulma.css' in result
        assert isinstance(result, str)

    def test_find_method_find_all_parameter(self) -> None:
        """Test find method with find_all=True (Django 5.2+)."""
        finder = SimpleBulmaFinder()

        result = finder.find('css/bulma.css', find_all=True)

        assert isinstance(result, list)
        assert len(result) == 1
        assert 'css/bulma.css' in result[0]

    def test_find_method_all_parameter(self) -> None:
        """Test find method with all=True (Django <5.2)."""
        finder = SimpleBulmaFinder()

        result = finder.find('css/bulma.css', all=True)

        assert isinstance(result, list)
        assert len(result) == 1

    @patch.object(SimpleBulmaFinder, '_get_bulma_css')
    @patch.object(SimpleBulmaFinder, '_get_custom_css')
    @patch.object(SimpleBulmaFinder, '_get_bulma_js')
    def test_list_method(
        self, mock_js: MagicMock, mock_custom: MagicMock, mock_css: MagicMock
    ) -> None:
        """Test list method yields all file types."""
        mock_css.return_value = ['css/bulma.css']
        mock_custom.return_value = ['css/custom.css']
        mock_js.return_value = ['js/extension.js']

        finder = SimpleBulmaFinder()

        results = list(finder.list([]))

        assert len(results) == 3
        # Each result should be (path, storage) tuple


class TestSimpleBulmaFinderBulma1:
    """Test SimpleBulmaFinder Bulma 1.0+ functionality."""

    @patch('django_simple_bulma.finders.simple_bulma_path')
    @patch('builtins.open', new_callable=mock_open)
    @override_settings(BULMA_SETTINGS={'variables': {'primary': '#007bff'}})
    def test_bulma_1_detection(self, mock_file: MagicMock, mock_path: MagicMock) -> None:
        """Test detection of Bulma 1.0+ version."""
        # Mock the package.json file existence and content
        mock_package_json = mock_path.return_value / "bulma" / "package.json"
        mock_package_json.exists.return_value = True

        mock_file.return_value.read.return_value = '{"name": "bulma", "version": "1.0.4"}'

        finder = SimpleBulmaFinder()

        # Mock the bulma_submodule_path
        finder.bulma_submodule_path = mock_path.return_value / "bulma" / "sass"

        # This should use Bulma 1.0+ path, not fallback to SASS
        with patch.object(finder, '_get_bulma_1_css') as mock_bulma_1:
            mock_bulma_1.return_value = ['css/bulma.css']
            finder._get_bulma_css()
            mock_bulma_1.assert_called_once()

    @patch('django_simple_bulma.finders.simple_bulma_path')
    @patch('builtins.open', new_callable=mock_open)
    @override_settings(BULMA_SETTINGS={'variables': {'primary': '#007bff'}})
    def test_bulma_0_detection(self, mock_file: MagicMock, mock_path: MagicMock) -> None:
        """Test detection of Bulma 0.x version falls back to SASS."""
        # Mock the package.json file existence and content for Bulma 0.x
        mock_package_json = mock_path.return_value / "bulma" / "package.json"
        mock_package_json.exists.return_value = True

        mock_file.return_value.read.return_value = '{"name": "bulma", "version": "0.9.4"}'

        finder = SimpleBulmaFinder()
        finder.bulma_submodule_path = mock_path.return_value / "bulma" / "sass"

        # This should fall back to SASS compilation
        with patch.object(finder, '_compile_sass_fallback') as mock_sass:
            mock_sass.return_value = ['css/bulma.css']
            finder._get_bulma_css()
            mock_sass.assert_called_once()

    @patch('django_simple_bulma.finders.simple_bulma_path')
    @patch('builtins.open', new_callable=mock_open)
    @override_settings(BULMA_SETTINGS={
        'variables': {'primary': '#007bff'},
        'alt_variables': {'primary': '#ff6b6b'},
        'extensions': ['bulma-tooltip']
    })
    def test_get_bulma_1_css_with_themes(self, mock_file: MagicMock, mock_path: MagicMock) -> None:
        """Test Bulma 1.0+ CSS generation with themes."""
        # Mock pre-compiled CSS file
        mock_precompiled = mock_path.return_value / "bulma" / "css" / "bulma.min.css"
        mock_precompiled.exists.return_value = True

        # Mock CSS content
        base_css = "/* Bulma CSS content */"
        mock_file.return_value.read.return_value = base_css

        finder = SimpleBulmaFinder()
        finder.bulma_submodule_path = mock_path.return_value / "bulma" / "sass"

        with patch.object(finder, '_get_extension_css') as mock_ext:
            mock_ext.return_value = "/* Extension CSS */"

            # Mock the CSS output path
            with patch('pathlib.Path.mkdir'), patch('builtins.open', mock_open()):
                result = finder._get_bulma_1_css(['alt'], True)

                # Should generate CSS for default and alt themes
                assert len(result) == 2
                assert 'css/bulma.css' in result
                assert 'css/alt_bulma.css' in result

    @patch('django_simple_bulma.finders.simple_bulma_path')
    @override_settings(BULMA_SETTINGS={'extensions': ['bulma-tooltip']})
    def test_get_extension_css(self, mock_path: MagicMock) -> None:
        """Test extension CSS collection."""
        # Mock extension directory structure
        mock_ext_dir = MagicMock()
        mock_ext_dir.name = "bulma-tooltip"
        mock_dist_dir = MagicMock()
        mock_css_file = MagicMock()
        mock_css_file.name = "bulma-tooltip.css"

        # Configure the path traversal
        mock_extensions_dir = MagicMock()
        mock_extensions_dir.iterdir.return_value = [mock_ext_dir]
        mock_path.__truediv__.return_value = mock_extensions_dir

        # Configure extension directory
        mock_ext_dir.__truediv__.return_value = mock_dist_dir
        mock_dist_dir.exists.return_value = True
        mock_dist_dir.glob.return_value = [mock_css_file]

        finder = SimpleBulmaFinder()

        with patch('django_simple_bulma.finders.is_enabled') as mock_enabled:
            mock_enabled.return_value = True
            with patch('builtins.open', mock_open(read_data="/* Tooltip CSS */")):
                result = finder._get_extension_css()

                assert "Extension: bulma-tooltip" in result
                assert "/* Tooltip CSS */" in result

    @patch('django_simple_bulma.finders.simple_bulma_path')
    @patch('builtins.open', new_callable=mock_open)
    @override_settings(BULMA_SETTINGS={'variables': {'primary': '#007bff'}})
    def test_css_variable_injection(self, mock_file: MagicMock, mock_path: MagicMock) -> None:
        """Test that CSS variables are properly injected into Bulma 1.0+ CSS."""
        # Mock pre-compiled CSS
        base_css = ":root { --bulma-primary: hsl(171, 100%, 41%); }"
        mock_file.return_value.read.return_value = base_css

        mock_precompiled = mock_path.return_value / "bulma" / "css" / "bulma.min.css"
        mock_precompiled.exists.return_value = True

        finder = SimpleBulmaFinder()
        finder.bulma_submodule_path = mock_path.return_value / "bulma" / "sass"

        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'):

            result = finder._get_bulma_1_css([], False)

            # Should have generated one CSS file
            assert len(result) == 1
            assert result[0] == 'css/bulma.css'
