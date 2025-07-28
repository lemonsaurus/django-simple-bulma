"""Tests for CSS variable conversion utilities."""
import pytest
from django_simple_bulma.css_variables import (
    convert_sass_variables_to_css,
    get_variable_mapping,
    hex_to_hsl,
    is_color_value,
)


class TestHexToHsl:
    """Test hex to HSL color conversion."""

    def test_basic_hex_colors(self) -> None:
        """Test conversion of basic hex colors."""
        # Bootstrap blue
        hue, saturation, lightness = hex_to_hsl("#007bff")
        assert hue == 211  # Allow for small rounding differences
        assert saturation == 100
        assert lightness == 50

        # Red
        hue, saturation, lightness = hex_to_hsl("#ff0000")
        assert hue == 0
        assert saturation == 100
        assert lightness == 50

        # Green
        hue, saturation, lightness = hex_to_hsl("#00ff00")
        assert hue == 120
        assert saturation == 100
        assert lightness == 50

    def test_named_colors(self) -> None:
        """Test conversion of named colors."""
        # White
        hue, saturation, lightness = hex_to_hsl("white")
        assert hue == 0
        assert saturation == 0
        assert lightness == 100

        # Black
        hue, saturation, lightness = hex_to_hsl("black")
        assert hue == 0
        assert saturation == 0
        assert lightness == 0

    def test_short_hex_format(self) -> None:
        """Test 3-character hex format."""
        hue, saturation, lightness = hex_to_hsl("#f00")  # Same as #ff0000
        assert hue == 0
        assert saturation == 100
        assert lightness == 50

    def test_hex_without_hash(self) -> None:
        """Test hex colors without # prefix."""
        hue, saturation, lightness = hex_to_hsl("ff0000")
        assert hue == 0
        assert saturation == 100
        assert lightness == 50

    def test_invalid_hex_color(self) -> None:
        """Test invalid hex color raises ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            hex_to_hsl("not-a-color")

        with pytest.raises(ValueError, match="Invalid hex color"):
            hex_to_hsl("#12345")  # Wrong length


class TestIsColorValue:
    """Test color value detection."""

    def test_hex_colors(self) -> None:
        """Test hex color detection."""
        assert is_color_value("#007bff") is True
        assert is_color_value("#ff6b6b") is True
        assert is_color_value("#fff") is True
        assert is_color_value("#000000") is True

    def test_named_colors(self) -> None:
        """Test named color detection."""
        assert is_color_value("white") is True
        assert is_color_value("black") is True
        assert is_color_value("red") is True
        assert is_color_value("Blue") is True  # Case insensitive

    def test_css_functions(self) -> None:
        """Test CSS color function detection."""
        assert is_color_value("hsl(210, 100%, 50%)") is True
        assert is_color_value("rgb(0, 123, 255)") is True
        assert is_color_value("hsla(210, 100%, 50%, 0.5)") is True
        assert is_color_value("rgba(0, 123, 255, 0.8)") is True

    def test_non_color_values(self) -> None:
        """Test non-color value detection."""
        assert is_color_value("Arial") is False
        assert is_color_value("1rem") is False
        assert is_color_value("bold") is False
        assert is_color_value("300") is False
        assert is_color_value("center") is False


class TestGetVariableMapping:
    """Test SASS to CSS variable mapping."""

    def test_mapping_structure(self) -> None:
        """Test that mapping returns expected structure."""
        mapping = get_variable_mapping()
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

    def test_common_variables(self) -> None:
        """Test mapping of commonly used variables."""
        mapping = get_variable_mapping()

        # Color variables
        assert mapping["primary"] == "--bulma-primary"
        assert mapping["link"] == "--bulma-link"
        assert mapping["info"] == "--bulma-info"
        assert mapping["success"] == "--bulma-success"
        assert mapping["warning"] == "--bulma-warning"
        assert mapping["danger"] == "--bulma-danger"

        # Typography
        assert mapping["family-primary"] == "--bulma-family-primary"
        assert mapping["family-secondary"] == "--bulma-family-secondary"

        # Sizes
        assert mapping["size-1"] == "--bulma-size-1"
        assert mapping["size-normal"] == "--bulma-size-normal"

    def test_all_values_are_css_variables(self) -> None:
        """Test that all mapped values are valid CSS variable names."""
        mapping = get_variable_mapping()
        for sass_var, css_var in mapping.items():
            assert css_var.startswith("--bulma-"), f"{sass_var} maps to invalid CSS var: {css_var}"


class TestConvertSassVariablesToCss:
    """Test SASS variable to CSS conversion."""

    def test_empty_variables(self) -> None:
        """Test conversion of empty variables dict."""
        result = convert_sass_variables_to_css({})
        assert result == ""

    def test_color_variable_conversion(self) -> None:
        """Test conversion of color variables."""
        variables = {"primary": "#007bff"}
        result = convert_sass_variables_to_css(variables)

        assert ":root {" in result
        assert "--bulma-primary-h: 211deg;" in result
        assert "--bulma-primary-s: 100%;" in result
        assert "--bulma-primary-l: 50%;" in result
        assert "}" in result

    def test_non_color_variable_conversion(self) -> None:
        """Test conversion of non-color variables."""
        variables = {"family-primary": "Arial", "size-1": "3rem"}
        result = convert_sass_variables_to_css(variables)

        assert ":root {" in result
        assert "--bulma-family-primary: Arial;" in result
        assert "--bulma-size-1: 3rem;" in result

    def test_mixed_variable_conversion(self) -> None:
        """Test conversion of mixed color and non-color variables."""
        variables = {
            "primary": "#007bff",
            "family-primary": "Arial",
            "size-1": "3rem"
        }
        result = convert_sass_variables_to_css(variables)

        # Should contain CSS variables for colors (HSL components)
        assert "--bulma-primary-h:" in result
        assert "--bulma-primary-s:" in result
        assert "--bulma-primary-l:" in result

        # Should contain direct mapping for non-colors
        assert "--bulma-family-primary: Arial;" in result
        assert "--bulma-size-1: 3rem;" in result

    def test_unmapped_variable_conversion(self) -> None:
        """Test conversion of variables not in mapping."""
        variables = {"custom-var": "some-value"}
        result = convert_sass_variables_to_css(variables)

        assert "--bulma-custom-var: some-value;" in result

    def test_named_color_conversion(self) -> None:
        """Test conversion of named colors."""
        variables = {"primary": "red"}
        result = convert_sass_variables_to_css(variables)

        assert "--bulma-primary-h: 0deg;" in result
        assert "--bulma-primary-s: 100%;" in result
        assert "--bulma-primary-l: 50%;" in result

    def test_invalid_color_fallback(self) -> None:
        """Test fallback for invalid color values."""
        variables = {"primary": "not-a-valid-color"}
        result = convert_sass_variables_to_css(variables)

        # Should fall back to direct assignment
        assert "--bulma-primary: not-a-valid-color;" in result

    def test_result_structure(self) -> None:
        """Test that result has proper CSS structure."""
        variables = {"primary": "#007bff"}
        result = convert_sass_variables_to_css(variables)

        # Should be properly formatted CSS
        assert result.startswith(":root {")
        assert result.endswith("}\n")
        assert result.count("{") == 1
        assert result.count("}") == 1
