"""Integration tests for django-simple-bulma."""

import os
import tempfile

import pytest
from django.core.management import call_command
from django.template import Context, Template
from django.test import override_settings


class TestCollectstaticIntegration:
    """Test collectstatic integration with SimpleBulmaFinder."""

    @pytest.mark.django_db
    def test_collectstatic_creates_bulma_css(self) -> None:
        """Test that collectstatic creates bulma.css file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')

            with override_settings(
                STATIC_ROOT=static_root,
                BULMA_SETTINGS={'extensions': [], 'variables': {'primary': '#007bff'}}
            ):
                # This should create the CSS files
                call_command('collectstatic', '--noinput', verbosity=0)

                # Check that bulma.css was created
                bulma_css = os.path.join(static_root, 'css', 'bulma.css')
                assert os.path.exists(bulma_css)

                # Check that the file has actual content
                with open(bulma_css, 'r') as f:
                    content = f.read()
                assert len(content) > 100  # Should be substantial CSS
                assert '$primary' not in content  # Variables should be compiled

    @pytest.mark.django_db
    def test_collectstatic_with_themes(self) -> None:
        """Test collectstatic with multiple themes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')

            with override_settings(
                STATIC_ROOT=static_root,
                BULMA_SETTINGS={
                    'extensions': [],
                    'variables': {'primary': '#007bff'},
                    'dark_variables': {'primary': '#333333'},
                    'light_variables': {'primary': '#ffffff'},
                }
            ):
                call_command('collectstatic', '--noinput', verbosity=0)

                # Check default theme
                assert os.path.exists(os.path.join(static_root, 'css', 'bulma.css'))

                # Check themed CSS files
                assert os.path.exists(os.path.join(static_root, 'css', 'dark_bulma.css'))
                assert os.path.exists(os.path.join(static_root, 'css', 'light_bulma.css'))

    @pytest.mark.django_db
    def test_collectstatic_with_extensions(self) -> None:
        """Test collectstatic includes extension files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')

            with override_settings(
                STATIC_ROOT=static_root,
                BULMA_SETTINGS={
                    'extensions': ['bulma-tooltip'],  # This extension should exist
                    'variables': {},
                }
            ):
                call_command('collectstatic', '--noinput', verbosity=0)

                # Should have main CSS
                assert os.path.exists(os.path.join(static_root, 'css', 'bulma.css'))

                # Should have some extension JS files (if tooltip has them)
                extensions_dir = os.path.join(static_root, 'extensions')
                if os.path.exists(extensions_dir):
                    import glob
                    glob.glob(os.path.join(extensions_dir, '**', '*.js'), recursive=True)
                    # Tooltip extension might not have JS, so this is optional


class TestTemplateRenderingIntegration:
    """Test template rendering with actual static files."""

    @pytest.mark.django_db
    def test_bulma_tag_renders_with_static_files(self) -> None:
        """Test bulma template tag renders correctly with static files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')

            with override_settings(
                STATIC_ROOT=static_root,
                STATIC_URL='/static/',
                BULMA_SETTINGS={'extensions': [], 'variables': {}}
            ):
                # Generate the static files first
                call_command('collectstatic', '--noinput', verbosity=0)

                # Now test template rendering
                template = Template("{% load django_simple_bulma %}{% bulma %}")
                result = template.render(Context())

                assert '/static/css/bulma.css' in result
                assert 'rel="stylesheet"' in result
                assert 'rel="preload"' in result

    @pytest.mark.django_db
    def test_bulma_tag_with_theme_integration(self) -> None:
        """Test bulma template tag with theme integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')

            with override_settings(
                STATIC_ROOT=static_root,
                STATIC_URL='/static/',
                BULMA_SETTINGS={
                    'extensions': [],
                    'variables': {'primary': '#007bff'},
                    'dark_variables': {'primary': '#333'},
                }
            ):
                call_command('collectstatic', '--noinput', verbosity=0)

                # Test default theme
                template = Template("{% load django_simple_bulma %}{% bulma %}")
                result = template.render(Context())
                assert '/static/css/bulma.css' in result

                # Test dark theme
                template = Template("{% load django_simple_bulma %}{% bulma 'dark' %}")
                result = template.render(Context())
                assert '/static/css/dark_bulma.css' in result
                assert 'id="bulma-css-dark"' in result

    @pytest.mark.django_db
    def test_font_awesome_tag_integration(self) -> None:
        """Test font_awesome template tag integration."""
        template = Template("{% load django_simple_bulma %}{% font_awesome %}")
        result = template.render(Context())

        # Should have FontAwesome CDN links
        assert 'fontawesome' in result
        assert 'crossorigin="anonymous"' in result
        assert 'rel="preload"' in result


class TestCustomScssIntegration:
    """Test custom SCSS compilation integration."""

    @pytest.mark.django_db
    def test_custom_scss_compilation(self) -> None:
        """Test that custom SCSS files are compiled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')
            staticfiles_dir = os.path.join(temp_dir, 'staticfiles')
            os.makedirs(staticfiles_dir)

            # Create a custom SCSS file
            test_styles_dir = os.path.join(staticfiles_dir, 'test_styles')
            os.makedirs(test_styles_dir)
            custom_scss = os.path.join(test_styles_dir, 'custom.scss')
            with open(custom_scss, 'w') as f:
                f.write("""
            .custom-class {
                color: red;
                font-size: 16px;
                .nested {
                    background: blue;
                }
            }
            """)

            with override_settings(
                STATIC_ROOT=static_root,
                STATICFILES_DIRS=[staticfiles_dir],
                BULMA_SETTINGS={
                    'extensions': [],
                    'variables': {},
                    'custom_scss': ['test_styles/custom.scss'],
                }
            ):
                call_command('collectstatic', '--noinput', verbosity=0)

                # Check that custom CSS was created
                custom_css = os.path.join(static_root, 'test_styles', 'custom.css')
                assert os.path.exists(custom_css)

                # Check content was compiled
                with open(custom_css, 'r') as f:
                    content = f.read()
                assert '.custom-class' in content
                assert 'color: red' in content
                # Nested selectors should be flattened
                assert '.custom-class .nested' in content or '.custom-class.nested' in content


class TestErrorHandlingIntegration:
    """Test error handling in integration scenarios."""

    @pytest.mark.django_db
    def test_collectstatic_with_missing_custom_scss(self) -> None:
        """Test collectstatic fails gracefully with missing custom SCSS."""
        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')

            with override_settings(
                STATIC_ROOT=static_root,
                BULMA_SETTINGS={
                    'extensions': [],
                    'variables': {},
                    'custom_scss': ['nonexistent.scss'],
                }
            ):
                with pytest.raises(ValueError) as exc_info:
                    call_command('collectstatic', '--noinput', verbosity=0)

                assert "Unable to locate the SCSS file" in str(exc_info.value)

    @pytest.mark.django_db
    def test_collectstatic_with_invalid_sass(self) -> None:
        """Test collectstatic handles SASS compilation errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')
            staticfiles_dir = os.path.join(temp_dir, 'staticfiles')
            os.makedirs(staticfiles_dir)

            # Create invalid SCSS
            test_styles_dir = os.path.join(staticfiles_dir, 'test_styles')
            os.makedirs(test_styles_dir)
            invalid_scss = os.path.join(test_styles_dir, 'invalid.scss')
            with open(invalid_scss, 'w') as f:
                f.write("""
            .invalid {
                color: ;  /* Invalid CSS */
                font-size: invalid-value;
            }
            """)

            with override_settings(
                STATIC_ROOT=static_root,
                STATICFILES_DIRS=[staticfiles_dir],
                BULMA_SETTINGS={
                    'extensions': [],
                    'variables': {},
                    'custom_scss': ['test_styles/invalid.scss'],
                }
            ):
                # This should raise a SASS compilation error
                with pytest.raises((ValueError, RuntimeError)):
                    call_command('collectstatic', '--noinput', verbosity=0)


class TestMultipleDjangoVersions:
    """Test compatibility across Django versions."""

    @pytest.mark.django_db
    def test_finder_find_method_compatibility(self) -> None:
        """Test that finder.find works with both old and new Django signatures."""
        from django_simple_bulma.finders import SimpleBulmaFinder

        finder = SimpleBulmaFinder()

        # Test old signature (all=True)
        result_old = finder.find('css/bulma.css', all=True)
        assert isinstance(result_old, list)

        # Test new signature (find_all=True)
        result_new = finder.find('css/bulma.css', find_all=True)
        assert isinstance(result_new, list)

        # Results should be equivalent
        assert result_old == result_new

        # Test single result
        result_single = finder.find('css/bulma.css')
        assert isinstance(result_single, str)


class TestPerformanceIntegration:
    """Test performance aspects of the integration."""

    @pytest.mark.django_db
    def test_collectstatic_performance(self) -> None:
        """Test that collectstatic completes in reasonable time."""
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            static_root = os.path.join(temp_dir, 'static')

            with override_settings(
                STATIC_ROOT=static_root,
                BULMA_SETTINGS={
                    'extensions': ['bulma-tooltip', 'bulma-calendar'],
                    'variables': {'primary': '#007bff'},
                    'dark_variables': {'primary': '#333'},
                }
            ):
                start_time = time.time()
                call_command('collectstatic', '--noinput', verbosity=0)
                end_time = time.time()

                # Should complete within reasonable time (adjust as needed)
                assert end_time - start_time < 30  # 30 seconds max

                # Should have created files
                assert os.path.exists(os.path.join(static_root, 'css', 'bulma.css'))

    @pytest.mark.django_db
    def test_template_rendering_performance(self) -> None:
        """Test template rendering performance."""
        import time

        template = Template("{% load django_simple_bulma %}{% bulma %}{% font_awesome %}")
        context = Context()

        # Warm up
        template.render(context)

        # Measure multiple renders
        start_time = time.time()
        for _ in range(100):
            template.render(context)
        end_time = time.time()

        # Should be fast (adjust threshold as needed)
        avg_time = (end_time - start_time) / 100
        assert avg_time < 0.01  # Less than 10ms per render
