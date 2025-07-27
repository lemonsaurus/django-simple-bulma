# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Commands

- **Install dev dependencies**: `pip install -e .[dev]`
- **Linting**: Run `flake8` (configured in `.flake8`)
- **Pre-commit hooks**: Run `pre-commit install` then `pre-commit run --all-files`
- **Collect static files**: `python manage.py collectstatic` (required after any Bulma configuration changes)

### Linting Configuration
The project uses flake8 with the following configuration:
- Max line length: 100
- Import order style: pycharm
- Inline quotes: double

Pre-commit hooks include:
- check-merge-conflict
- check-yaml
- end-of-file-fixer
- trailing-whitespace
- python-check-blanket-noqa
- flake8

## High-Level Architecture

### Core Components

1. **SimpleBulmaFinder** (`django_simple_bulma/finders.py`): Custom Django static file finder that:
   - Compiles Bulma SASS files with user-defined variables
   - Handles multiple themes via `*_variables` dictionaries
   - Compiles custom SCSS files specified by users
   - Bundles JavaScript files from enabled extensions
   - Integrates with Django's `collectstatic` command

2. **Template Tags** (`django_simple_bulma/templatetags/django_simple_bulma.py`):
   - `{% bulma %}`: Loads compiled CSS and JS for Bulma
   - `{% font_awesome %}`: Loads FontAwesome (v6+ with token or v5.14.0 fallback)

3. **Configuration** (in Django `settings.py`):
   ```python
   BULMA_SETTINGS = {
       "extensions": ["bulma-calendar", "bulma-tooltip"],  # or "all"
       "variables": {"primary": "#000000"},  # SASS variables
       "alt_variables": {"primary": "#fff"},  # Alternative themes
       "output_style": "compressed",  # CSS output style
       "fontawesome_token": "your_token",  # FontAwesome v6+ kit
       "custom_scss": ["path/to/custom.scss"],  # Custom SCSS files
   }
   ```

### File Structure

- `django_simple_bulma/bulma/`: Bulma source files (git submodule)
- `django_simple_bulma/extensions/`: Bulma extensions
- `django_simple_bulma/css/`: Compiled CSS output
- `django_simple_bulma/utils.py`: Helper functions for extension management

### Key Design Decisions

1. **SASS Compilation**: Uses `libsass` (not `sass`) to compile SCSS at collection time
2. **Theme Support**: Multiple themes can be defined using `*_variables` pattern
3. **Extension Management**: Extensions are automatically discovered and included
4. **Static File Integration**: Works seamlessly with Django's static file system

### Critical Implementation Details

- The finder rebuilds CSS files during `collectstatic`, not at runtime
- JavaScript inclusion can be controlled with `include_js=False` to prevent duplicates
- Custom SCSS files are resolved using Django's other configured finders
- The package conflicts with the `sass` module - only `libsass` should be installed
