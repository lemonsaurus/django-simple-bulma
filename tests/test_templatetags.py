"""Tests for django_simple_bulma template tags."""

import pytest
from django.template import Context, Template
from django.test import override_settings
from unittest.mock import patch, MagicMock

from django_simple_bulma.templatetags.django_simple_bulma import bulma, font_awesome


class TestBulmaTemplateTag:
    """Test the {% bulma %} template tag."""

    @pytest.mark.django_db
    def test_bulma_tag_default_theme(self):
        """Test bulma tag with default theme."""
        template = Template("{% load django_simple_bulma %}{% bulma %}")
        result = template.render(Context())
        
        assert '<link rel="preload" href="/static/css/bulma.css" as="style">' in result
        assert '<link rel="stylesheet" href="/static/css/bulma.css" id="bulma-css">' in result
        assert 'defer type="text/javascript"' in result

    @pytest.mark.django_db
    @override_settings(BULMA_SETTINGS={'dark_variables': {'primary': '#333'}})
    def test_bulma_tag_with_theme(self):
        """Test bulma tag with specific theme."""
        template = Template("{% load django_simple_bulma %}{% bulma 'dark' %}")
        result = template.render(Context())
        
        assert '<link rel="preload" href="/static/css/dark_bulma.css" as="style">' in result
        assert '<link rel="stylesheet" href="/static/css/dark_bulma.css" id="bulma-css-dark">' in result

    @pytest.mark.django_db
    def test_bulma_tag_without_js(self):
        """Test bulma tag with include_js=False."""
        template = Template("{% load django_simple_bulma %}{% bulma include_js=False %}")
        result = template.render(Context())
        
        assert '<link rel="preload" href="/static/css/bulma.css" as="style">' in result
        assert '<link rel="stylesheet" href="/static/css/bulma.css" id="bulma-css">' in result
        assert 'script' not in result

    @pytest.mark.django_db
    @patch('django_simple_bulma.utils.logger')
    def test_bulma_tag_invalid_theme_warning(self, mock_logger):
        """Test bulma tag logs warning for invalid theme."""
        template = Template("{% load django_simple_bulma %}{% bulma 'nonexistent' %}")
        result = template.render(Context())
        
        # Should fall back to default theme
        assert '<link rel="stylesheet" href="/static/css/bulma.css" id="bulma-css">' in result
        mock_logger.warning.assert_called_once()
        assert "Theme 'nonexistent' does not match" in mock_logger.warning.call_args[0][0]

    @pytest.mark.django_db
    @override_settings(BULMA_SETTINGS={'dark_variables': {'primary': '#333'}, 'light_variables': {'primary': '#fff'}})
    def test_bulma_tag_with_valid_theme(self):
        """Test bulma tag with valid theme from themes list."""
        template = Template("{% load django_simple_bulma %}{% bulma 'dark' %}")
        result = template.render(Context())
        
        assert '<link rel="stylesheet" href="/static/css/dark_bulma.css" id="bulma-css-dark">' in result

    @pytest.mark.django_db
    @patch('django_simple_bulma.utils.get_js_files')
    def test_bulma_tag_js_files(self, mock_get_js_files):
        """Test bulma tag includes JS files from get_js_files."""
        mock_get_js_files.return_value = ['extensions/test.min.js', 'extensions/other.js']
        
        template = Template("{% load django_simple_bulma %}{% bulma %}")
        result = template.render(Context())
        
        assert '<script defer type="text/javascript" src="/static/extensions/test.min.js"></script>' in result
        assert '<script defer type="text/javascript" src="/static/extensions/other.js"></script>' in result


class TestFontAwesomeTemplateTag:
    """Test the {% font_awesome %} template tag."""

    @pytest.mark.django_db
    @override_settings(BULMA_SETTINGS={'fontawesome_token': 'test_token_123'})
    def test_font_awesome_with_token(self):
        """Test font_awesome tag with configured token."""
        template = Template("{% load django_simple_bulma %}{% font_awesome %}")
        result = template.render(Context())
        
        assert 'https://kit.fontawesome.com/test_token_123.js' in result
        assert 'crossorigin="anonymous"' in result
        assert 'rel="preload"' in result
        assert 'defer' in result

    @pytest.mark.django_db
    @override_settings(BULMA_SETTINGS={})
    def test_font_awesome_without_token(self):
        """Test font_awesome tag falls back to v5.14.0 when no token."""
        template = Template("{% load django_simple_bulma %}{% font_awesome %}")
        result = template.render(Context())
        
        assert 'https://use.fontawesome.com/releases/v5.14.0/css/all.css' in result
        assert 'integrity="sha384-HzLeBuhoNPvSl5KYnjx0BT+WB0QEEqLprO+NBkkk5gbc67FTaL7XIGa2w1L0Xbgc"' in result
        assert 'crossorigin="anonymous"' in result

    @pytest.mark.django_db
    def test_font_awesome_returns_safe_string(self):
        """Test font_awesome returns SafeString."""
        result = font_awesome()
        from django.utils.safestring import SafeString
        assert isinstance(result, SafeString)

    @pytest.mark.django_db
    @override_settings(BULMA_SETTINGS={'fontawesome_token': ''})
    def test_font_awesome_empty_token(self):
        """Test font_awesome with empty token uses fallback."""
        result = font_awesome()
        
        assert 'v5.14.0' in str(result)
        assert 'kit.fontawesome.com' not in str(result)


class TestTemplateTagIntegration:
    """Integration tests for template tags."""

    @pytest.mark.django_db
    def test_both_tags_in_template(self):
        """Test using both bulma and font_awesome tags together."""
        template = Template("""
        {% load django_simple_bulma %}
        {% bulma %}
        {% font_awesome %}
        """)
        result = template.render(Context())
        
        assert 'bulma.css' in result
        assert 'fontawesome' in result

    @pytest.mark.django_db
    def test_multiple_bulma_calls_with_without_js(self):
        """Test calling bulma tag multiple times with different js settings."""
        template = Template("""
        {% load django_simple_bulma %}
        {% bulma %}
        {% bulma include_js=False %}
        """)
        result = template.render(Context())
        
        # Should have CSS twice but JS only once
        assert result.count('bulma.css') == 4  # 2 preload + 2 stylesheet
        # JS should appear for first call only
        lines = result.split('\n')
        js_lines = [line for line in lines if 'script' in line and 'defer' in line]
        assert len(js_lines) > 0  # Should have at least some JS from first call