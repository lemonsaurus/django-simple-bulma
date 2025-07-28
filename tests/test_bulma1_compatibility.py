"""Integration tests for Bulma 1.0+ backwards compatibility."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings
from django_simple_bulma.finders import SimpleBulmaFinder


class TestBulka1BackwardsCompatibility:
    """Test that existing BULMA_SETTINGS configurations work with Bulma 1.0+."""

    @override_settings(BULMA_SETTINGS={
        'variables': {'primary': '#007bff', 'family-primary': 'Arial'},
        'extensions': []
    })
    def test_basic_theme_compatibility(self) -> None:
        """Test that basic theme configuration from 2.x works with Bulma 1.0+."""
        finder = SimpleBulmaFinder()

        # Mock Bulma 1.0+ environment
        with patch.object(finder, 'bulma_submodule_path') as mock_path:
            mock_path.parent = Path('/mock/bulma')

            # Mock package.json for Bulma 1.0+
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True

                with patch('builtins.open') as mock_open:
                    # Mock package.json content
                    mock_open.return_value.__enter__.return_value.read.return_value = \
                        '{"name": "bulma", "version": "1.0.4"}'

                    # Mock pre-compiled CSS
                    with patch.object(finder, '_get_bulma_1_css') as mock_bulma1:
                        mock_bulma1.return_value = ['css/bulma.css']

                        result = finder._get_bulma_css()

                        # Should use Bulma 1.0+ method
                        mock_bulma1.assert_called_once()
                        assert result == ['css/bulma.css']

    @override_settings(BULMA_SETTINGS={
        'variables': {'primary': '#007bff'},
        'alt_variables': {'primary': '#ff6b6b', 'link': '#28a745'},
        'extensions': []
    })
    def test_multi_theme_compatibility(self) -> None:
        """Test that multi-theme configurations work with Bulma 1.0+."""
        finder = SimpleBulmaFinder()

        with patch.object(finder, 'bulma_submodule_path') as mock_submodule_path:
            mock_parent = MagicMock()
            mock_submodule_path.parent = mock_parent
            mock_precompiled = MagicMock()
            mock_parent.__truediv__.return_value.__truediv__.return_value = mock_precompiled
            mock_precompiled.exists.return_value = True

            with patch('builtins.open') as mock_open:
                # Mock reading pre-compiled CSS
                mock_open.return_value.__enter__.return_value.read.return_value = \
                    ":root { --bulma-primary: hsl(171, 100%, 41%); }"

                with patch('pathlib.Path.mkdir'), \
                     patch('pathlib.Path.write_text'):

                    result = finder._get_bulma_1_css(['alt'], False)

                    # Should generate CSS for both default and alt themes
                    assert len(result) == 2
                    assert 'css/bulma.css' in result
                    assert 'css/alt_bulma.css' in result

    @override_settings(BULMA_SETTINGS={
        'variables': {'primary': '#007bff'},
        'extensions': ['bulma-tooltip', 'bulma-calendar']
    })
    def test_extension_compatibility(self) -> None:
        """Test that extension configurations work with Bulma 1.0+."""
        finder = SimpleBulmaFinder()

        with patch.object(finder, 'bulma_submodule_path') as mock_submodule_path:
            mock_parent = MagicMock()
            mock_submodule_path.parent = mock_parent

            # Mock Bulma 1.0+ version detection
            mock_package_json = MagicMock()
            mock_parent.__truediv__.return_value = mock_package_json
            mock_package_json.exists.return_value = True

            with patch('builtins.open') as mock_open:
                # Mock package.json content for Bulma 1.0+
                mock_open.return_value.__enter__.return_value.read.return_value = \
                    '{"name": "bulma", "version": "1.0.4"}'

                with patch.object(finder, '_get_bulma_1_css') as mock_bulma1:
                    mock_bulma1.return_value = ['css/bulma.css']

                    # This should detect Bulma 1.0+ and call _get_bulma_1_css
                    finder._get_bulma_css()

                    # Verify the method was called with extensions enabled
                    mock_bulma1.assert_called_once()
                    call_args = mock_bulma1.call_args[0]
                    themes, has_extensions = call_args
                    assert has_extensions is True

    def test_css_variable_generation_matches_sass_expectations(self) -> None:
        """Test that CSS variables generated match what SASS variables would produce."""
        from django_simple_bulma.css_variables import convert_sass_variables_to_css

        # Test common variable configurations that users might have
        test_cases = [
            # Bootstrap-like theme
            {
                'primary': '#007bff',
                'success': '#28a745',
                'danger': '#dc3545',
                'family-primary': 'system-ui, -apple-system, sans-serif'
            },
            # Custom brand theme
            {
                'primary': '#6f42c1',
                'link': '#6f42c1',
                'family-primary': 'Poppins, sans-serif',
                'radius': '8px'
            },
            # Minimalist theme
            {
                'primary': '#000000',
                'family-primary': 'Inter, sans-serif',
                'size-1': '2.5rem'
            }
        ]

        for variables in test_cases:
            result = convert_sass_variables_to_css(variables)

            # Should generate valid CSS
            assert result.startswith(':root {')
            assert result.endswith('}\n')

            # Should contain CSS variables for all input variables
            for sass_var, value in variables.items():
                # Color variables get expanded to HSL components
                if sass_var in ['primary', 'success', 'danger', 'link'] and value.startswith('#'):
                    assert f'--bulma-{sass_var}-h:' in result
                    assert f'--bulma-{sass_var}-s:' in result
                    assert f'--bulma-{sass_var}-l:' in result
                else:
                    # Non-color variables map directly
                    assert f'--bulma-{sass_var}: {value};' in result

    @override_settings(BULMA_SETTINGS={})
    def test_no_settings_still_works(self) -> None:
        """Test that Bulma 1.0+ works even with no custom settings."""
        finder = SimpleBulmaFinder()

        with patch.object(finder, 'bulma_submodule_path') as mock_submodule_path:
            mock_parent = MagicMock()
            mock_submodule_path.parent = mock_parent
            mock_precompiled = MagicMock()
            mock_parent.__truediv__.return_value.__truediv__.return_value = mock_precompiled
            mock_precompiled.exists.return_value = True

            with patch('builtins.open') as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = \
                    ":root { --bulma-primary: hsl(171, 100%, 41%); }"

                with patch('pathlib.Path.mkdir'), \
                     patch('pathlib.Path.write_text'):

                    result = finder._get_bulma_1_css([], False)

                    # Should still generate basic CSS file
                    assert len(result) == 1
                    assert result[0] == 'css/bulma.css'

    def test_error_handling_missing_precompiled_css(self) -> None:
        """Test error handling when pre-compiled CSS is missing."""
        finder = SimpleBulmaFinder()

        with patch.object(finder, 'bulma_submodule_path') as mock_submodule_path:
            mock_parent = MagicMock()
            mock_submodule_path.parent = mock_parent
            mock_precompiled = MagicMock()
            mock_parent.__truediv__.return_value.__truediv__.return_value = mock_precompiled
            mock_precompiled.exists.return_value = False

            with pytest.raises(FileNotFoundError, match="Pre-compiled Bulma CSS not found"):
                finder._get_bulma_1_css([], False)

    @override_settings(BULMA_SETTINGS={
        'variables': {'primary': 'not-a-valid-color'},
        'extensions': []
    })
    def test_invalid_color_fallback(self) -> None:
        """Test that invalid color values fall back gracefully."""
        from django_simple_bulma.css_variables import convert_sass_variables_to_css

        variables = {'primary': 'not-a-valid-color'}
        result = convert_sass_variables_to_css(variables)

        # Should fall back to direct assignment instead of HSL conversion
        assert '--bulma-primary: not-a-valid-color;' in result
        # Should NOT contain HSL components
        assert '--bulma-primary-h:' not in result
        assert '--bulma-primary-s:' not in result
        assert '--bulma-primary-l:' not in result
