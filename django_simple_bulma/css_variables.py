"""
CSS Variable transformation utilities for Bulma 1.0+ compatibility.

This module handles the conversion from legacy SASS variables (used in django-simple-bulma 2.x)
to the new CSS variable system introduced in Bulma 1.0+. This allows existing themes and
customizations to continue working without breaking changes.
"""
import re

# Vars Bulma 1.x exposes as direct color values, not HSL channels. Setting
# `--bulma-white-h/s/l` does nothing because Bulma reads `--bulma-white`
# as a single color. Skip the HSL split for these.
_DIRECT_COLOR_VARS = frozenset({"white", "black", "light", "dark"})


def get_hsl_channel_names(sass_var: str) -> tuple[str, str, str]:
    """
    Return the HSL CSS variable names Bulma expects for a SASS color variable.

    Most colors follow `--bulma-{name}-h/s/l`, but scheme and hero share
    hue/saturation across variants, only lightness is per-variant. These
    special cases must match Bulma 1.x's internal naming for the cascade
    to actually apply the user's color.
    """
    # Scheme: --bulma-scheme-h / -s are shared, lightness is per-variant
    # (scheme-main, scheme-main-bis, scheme-main-ter, scheme-invert, ...)
    if sass_var == "scheme" or sass_var.startswith("scheme-"):
        return ("--bulma-scheme-h", "--bulma-scheme-s", f"--bulma-{sass_var}-l")

    # Hero: --bulma-hero-h / -s are shared; Bulma defines
    # --bulma-hero-background-l and --bulma-hero-color-l
    if sass_var in ("hero", "hero-background", "hero-color"):
        if sass_var == "hero":
            l_name = "--bulma-hero-background-l"
        else:
            l_name = f"--bulma-{sass_var}-l"
        return ("--bulma-hero-h", "--bulma-hero-s", l_name)

    base = f"--bulma-{sass_var}"
    return (f"{base}-h", f"{base}-s", f"{base}-l")


def hex_to_hsl(hex_color: str) -> tuple[int, int, int]:
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
    # Extended set based on CSS Color Module Level 4 for broader compatibility
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
        'lime': '#00ff00',
        'aqua': '#00ffff',
        'fuchsia': '#ff00ff',
        'maroon': '#800000',
        'navy': '#000080',
        'olive': '#808000',
        'silver': '#c0c0c0',
        'teal': '#008080',
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
    # Hex color - strict validation for 3 or 6 character hex values
    if re.match(r'^#[0-9a-fA-F]{3}$', value) or re.match(r'^#[0-9a-fA-F]{6}$', value):
        return True

    # Named colors - extended set for broader compatibility
    named_colors = {
        'white', 'black', 'red', 'green', 'blue', 'yellow',
        'cyan', 'magenta', 'orange', 'purple', 'pink', 'brown',
        'gray', 'grey', 'lime', 'aqua', 'fuchsia', 'maroon',
        'navy', 'olive', 'silver', 'teal'
    }
    if value.lower() in named_colors:
        return True

    # HSL/RGB functions
    if re.match(r'^(hsl|rgb|hsla|rgba)\s*\(', value.lower()):
        return True

    return False


def get_variable_mapping() -> dict[str, str]:
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


def convert_sass_variables_to_css(variables: dict[str, str]) -> str:
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
        # Some scheme colors (white/black/light/dark) are direct color
        # values in Bulma 1.x, not HSL channels. Emit them as a single var.
        if sass_var in _DIRECT_COLOR_VARS:
            css_var = variable_mapping.get(sass_var, f"--bulma-{sass_var}")
            css_declarations.append(f"  {css_var}: {value};")
            continue

        # Handle color values specially: set the HSL channels Bulma expects.
        if is_color_value(value):
            try:
                hue, saturation, lightness = hex_to_hsl(value)
                h_var, s_var, l_var = get_hsl_channel_names(sass_var)
                css_declarations.extend([
                    f"  {h_var}: {hue}deg;",
                    f"  {s_var}: {saturation}%;",
                    f"  {l_var}: {lightness}%;",
                ])
            except (ValueError, TypeError):
                # If color conversion fails, fall back to the mapped var name.
                css_var = variable_mapping.get(sass_var, f"--bulma-{sass_var}")
                css_declarations.append(f"  {css_var}: {value};")
        else:
            # Non-color values can be used directly
            css_var = variable_mapping.get(sass_var, f"--bulma-{sass_var}")
            css_declarations.append(f"  {css_var}: {value};")

    if css_declarations:
        return ":root {\n" + "\n".join(css_declarations) + "\n}\n"

    return ""
