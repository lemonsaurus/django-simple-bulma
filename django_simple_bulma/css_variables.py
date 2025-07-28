"""
CSS Variable transformation utilities for Bulma 1.0+ compatibility.

This module handles the conversion from legacy SASS variables (used in django-simple-bulma 2.x)
to the new CSS variable system introduced in Bulma 1.0+. This allows existing themes and
customizations to continue working without breaking changes.
"""
import re
from typing import Dict, Tuple


def hex_to_hsl(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to HSL values.

    Args:
        hex_color: Hex color string (e.g., "#007bff", "#ff6b6b", "blue")

    Returns:
        Tuple of (hue, saturation, lightness) where:
        - hue is 0-360 degrees
        - saturation is 0-100 percent
        - lightness is 0-100 percent
    """
    # Handle named colors - convert to hex first
    named_colors = {
        'white': '#ffffff',
        'black': '#000000',
        'red': '#ff0000',
        'green': '#00ff00',
        'blue': '#0000ff',
        'yellow': '#ffff00',
        'cyan': '#00ffff',
        'magenta': '#ff00ff',
        'orange': '#ffa500',
        'purple': '#800080',
        'pink': '#ffc0cb',
        'brown': '#a52a2a',
        'gray': '#808080',
        'grey': '#808080',
    }

    # Normalize hex color
    if hex_color.lower() in named_colors:
        hex_color = named_colors[hex_color.lower()]

    # Remove # if present
    hex_color = hex_color.lstrip('#')

    # Handle 3-character hex
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])

    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")

    # Convert to RGB
    red = int(hex_color[0:2], 16) / 255.0
    green = int(hex_color[2:4], 16) / 255.0
    blue = int(hex_color[4:6], 16) / 255.0

    # Convert RGB to HSL
    max_val = max(red, green, blue)
    min_val = min(red, green, blue)
    diff = max_val - min_val

    # Lightness
    lightness = (max_val + min_val) / 2.0

    if diff == 0:
        hue = saturation = 0  # achromatic
    else:
        # Saturation
        if lightness < 0.5:
            saturation = diff / (max_val + min_val)
        else:
            saturation = diff / (2.0 - max_val - min_val)

        # Hue
        if max_val == red:
            hue = (green - blue) / diff + (6 if green < blue else 0)
        elif max_val == green:
            hue = (blue - red) / diff + 2
        else:
            hue = (red - green) / diff + 4
        hue /= 6.0

    return (
        round(hue * 360),
        round(saturation * 100),
        round(lightness * 100)
    )


def is_color_value(value: str) -> bool:
    """
    Check if a value represents a color (hex, named color, etc.).

    Args:
        value: String value to check

    Returns:
        True if the value appears to be a color
    """
    # Hex color
    if re.match(r'^#[0-9a-fA-F]{3,6}$', value):
        return True

    # Named colors
    named_colors = {
        'white', 'black', 'red', 'green', 'blue', 'yellow',
        'cyan', 'magenta', 'orange', 'purple', 'pink', 'brown',
        'gray', 'grey'
    }
    if value.lower() in named_colors:
        return True

    # HSL/RGB functions
    if re.match(r'^(hsl|rgb|hsla|rgba)\s*\(', value.lower()):
        return True

    return False


def get_variable_mapping() -> Dict[str, str]:
    """
    Get mapping from legacy SASS variable names to Bulma 1.0+ CSS variables.

    Returns:
        Dictionary mapping SASS variable names to CSS variable names
    """
    return {
        # Primary color palette - most common customizations
        'primary': '--bulma-primary',
        'link': '--bulma-link',
        'info': '--bulma-info',
        'success': '--bulma-success',
        'warning': '--bulma-warning',
        'danger': '--bulma-danger',

        # Scheme colors
        'white': '--bulma-white',
        'black': '--bulma-black',
        'light': '--bulma-light',
        'dark': '--bulma-dark',

        # Typography
        'family-primary': '--bulma-family-primary',
        'family-secondary': '--bulma-family-secondary',
        'family-code': '--bulma-family-code',

        # Sizes
        'size-1': '--bulma-size-1',
        'size-2': '--bulma-size-2',
        'size-3': '--bulma-size-3',
        'size-4': '--bulma-size-4',
        'size-5': '--bulma-size-5',
        'size-6': '--bulma-size-6',
        'size-7': '--bulma-size-7',
        'size-small': '--bulma-size-small',
        'size-normal': '--bulma-size-normal',
        'size-medium': '--bulma-size-medium',
        'size-large': '--bulma-size-large',

        # Weights
        'weight-light': '--bulma-weight-light',
        'weight-normal': '--bulma-weight-normal',
        'weight-medium': '--bulma-weight-medium',
        'weight-semibold': '--bulma-weight-semibold',
        'weight-bold': '--bulma-weight-bold',
        'weight-extrabold': '--bulma-weight-extrabold',

        # Border radius
        'radius': '--bulma-radius',
        'radius-small': '--bulma-radius-small',
        'radius-medium': '--bulma-radius-medium',
        'radius-large': '--bulma-radius-large',
        'radius-rounded': '--bulma-radius-rounded',

        # Spacing
        'block-spacing': '--bulma-block-spacing',

        # Animation
        'duration': '--bulma-duration',
        'easing': '--bulma-easing',
        'speed': '--bulma-speed',
    }


def convert_sass_variables_to_css(variables: Dict[str, str]) -> str:
    """
    Convert legacy SASS variables to CSS variable declarations.

    Args:
        variables: Dictionary of SASS variable names to values

    Returns:
        CSS string with :root declarations for the CSS variables
    """
    if not variables:
        return ""

    variable_mapping = get_variable_mapping()
    css_declarations = []

    for sass_var, value in variables.items():
        # Get the corresponding CSS variable name
        css_var = variable_mapping.get(sass_var)
        if not css_var:
            # For unmapped variables, try to convert the name directly
            css_var = f"--bulma-{sass_var}"

        # Handle color values specially
        if is_color_value(value):
            try:
                hue, saturation, lightness = hex_to_hsl(value)
                # For colors, we need to set the HSL components
                css_declarations.extend([
                    f"  {css_var}-h: {hue}deg;",
                    f"  {css_var}-s: {saturation}%;",
                    f"  {css_var}-l: {lightness}%;",
                ])
            except (ValueError, TypeError):
                # If color conversion fails, use the value directly
                css_declarations.append(f"  {css_var}: {value};")
        else:
            # Non-color values can be used directly
            css_declarations.append(f"  {css_var}: {value};")

    if css_declarations:
        return ":root {\n" + "\n".join(css_declarations) + "\n}\n"

    return ""
