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
        """Test error when sass module is installed instead of libsass."""
        # Remove libsass_version to simulate sass module
        delattr(mock_sass, 'libsass_version')

        finder = SimpleBulmaFinder()

        with pytest.raises(UserWarning) as exc_info:
            finder._get_bulma_css()

        assert "sass` module installed" in str(exc_info.value)
        assert "libsass` module" in str(exc_info.value)

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
        for path, storage in results:
            assert isinstance(path, str)
            assert isinstance(storage, FileSystemStorage)

        paths = [path for path, _ in results]
        assert 'css/bulma.css' in paths
        assert 'css/custom.css' in paths
        assert 'js/extension.js' in paths
