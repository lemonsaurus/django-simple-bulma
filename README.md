django-simple-bulma
===================
`django-simple-bulma` is a Django application that makes [Bulma](https://bulma.io)
and various Bulma add-ons and extensions available to use in your Django project with as little setup as
possible. The goal of this project is to make it as easy as possible to use Bulma with Django.

This project currently uses **Bulma v1.0.4**, and is automatically updated with every new release. **Version 3.0** represents a major upgrade that focuses on actively maintained extensions and Bulma 1.0+ compatibility. If a new version has come out with features you'd like to make use of, please [create an issue](https://github.com/python-discord/django-simple-bulma/issues), and we will be happy to make a release to update it.

Installation
------------
To get `django-simple-bulma`, up and running for your Django project, follow these simple steps:

- Install it from PyPI with `pip install django-simple-bulma` (or add it to
  your [Pipfile](https://pipenv.readthedocs.io/en/latest/))
- In your Django projects `settings.py` file:
  - Add `django_simple_bulma` to your `INSTALLED_APPS`
    ```python
    INSTALLED_APPS = [
      # ...
      'django_simple_bulma',
      # ...
    ]
    ```
  - Add `django_simple_bulma.finders.SimpleBulmaFinder` to your `STATICFILES_FINDERS`. This normally holds two default
    handlers that you will probably want to keep, so unless you have any other custom Finders, it should look like this:
    ```python
    STATICFILES_FINDERS = [
      # First add the two default Finders, since this will overwrite the default.
      'django.contrib.staticfiles.finders.FileSystemFinder',
      'django.contrib.staticfiles.finders.AppDirectoriesFinder',

      # Now add our custom SimpleBulma one.
      'django_simple_bulma.finders.SimpleBulmaFinder',
    ]
    ```
- Run `python manage.py collectstatic` command in order to build Bulma and move it to your `staticfiles` folder. Please
  note that you will need to use this command every time you make a change to the configuration, as this is the only way
  to rebuild the Bulma css file. If you are not using `collectstatic`
  , [read up on it](https://stackoverflow.com/questions/34586114/whats-the-point-of-djangos-collectstatic)
  and [start using it](https://docs.djangoproject.com/en/2.1/ref/contrib/staticfiles/).

  This app works fine with [Whitenoise](http://whitenoise.evans.io/en/stable/), which is a great way to serve static
  files without needing to mess with your webserver.

`django-simple-bulma` should now be working! In order to import it into your template, first load the app
with `{% load django_simple_bulma %}`, and then use the `{% bulma %}` template tag. If you're planning on using icons,
you might also want to import FontAwesome by using `{% font_awesome %}`.

  ```html
<head>
  <!-- ... -->
  {% load django_simple_bulma %}
  {% bulma %}
  {% font_awesome %}
  <!-- ... -->
</head>
  ```

- You're all set! Any Bulma classes you apply should now be working!

Customization
-------------
Bulma looks nice by default, but most users will want to customize its look and feel. For this, we've provided a super
simple way to change the [Bulma variables](https://bulma.io/documentation/customize/list-of-sass-variables/) and to choose
which [Bulma extensions](https://wikiki.github.io/) you want to load into your project.

In order to do this, we'll simply create a dictionary inside your `settings.py` called `BULMA_SETTINGS`, and configure
it there. Here's an example of what that looks like:

```python
# Custom settings for django-simple-bulma
BULMA_SETTINGS = {
  "extensions": [
    "bulma-calendar",
    "bulma-tooltip",
  ],
  "variables": {
    "primary": "#000000",
    "size-1": "6rem",
  },
  "alt_variables": {
    "primary": "#fff",
    "scheme-main": "#000",
  },
  "output_style": "compressed",
  "fontawesome_token": "e761a01be3",
}
```

You may here define any variable found on the [Bulma variables](https://bulma.io/documentation/customize/variables/)
page, and you may use any valid SASS or CSS as the value. For example, `hsl(217, 71%, 53%)` would be a valid value for a
color variable, as would `#ffff00`. Please note that any syntactically incorrect values may prevent Bulma from building
correctly, so be careful what you add here unless you know exactly what you're doing.

#### Multiple themes

If you want multiple different configurations of variables, then you should define them as separate themes. Define a new
theme by providing a key that matches the regex `\w+_variables` (e.g. `alt_variables` or `dark_variables`), unique
stylesheets will then be generated using the variables at that key.

To use these stylesheets in a template, pass the theme name to the `{% bulma %}` tag either as a
string `{% bulma 'alt' %}` or as a template variable `{% bulma theme %}`. When calling the `bulma` template
more than once in the same document (for example for implementing a dark theme switch), you will want to pass `include_js=False` to
at least one of these to prevent duplicate loading of JavaScript resources.

#### Extensions

If the `extensions` key is not found, it will default to not loading any extensions. If you want all extensions, simply
set it to the string `"all"`.

We currently support these actively maintained extensions compatible with Bulma 1.0+:

- [bulma-calendar](https://github.com/michael-hack/bulma-calendar) - Calendar and datepicker components (v7.1.1+)
- [bulma-tooltip](https://github.com/CreativeBulma/bulma-tooltip) - Tooltip components (v1.2.0+)
- [bulma-responsive-tables](https://github.com/justboil/bulma-responsive-tables) - Responsive table components for mobile-friendly tables
- [bulma-switch-control](https://github.com/justboil/bulma-switch-control) - Switch/toggle control components
- [bulma-radio](https://github.com/justboil/bulma-radio) - Enhanced radio button components
- [bulma-checkbox](https://github.com/justboil/bulma-checkbox) - Enhanced checkbox components  
- [bulma-upload-control](https://github.com/justboil/bulma-upload-control) - File upload control components

**Note**: As of this version, we have streamlined our extension support to focus only on actively maintained, Bulma 1.0+ compatible extensions. Many of the previously supported extensions are no longer maintained or compatible with modern Bulma versions.

If an extension you want to use is missing, feel free
to [create an issue](https://github.com/python-discord/django-simple-bulma/issues) and we will be happy to add it.
Alternatively, add it yourself and create a pull request (
see [this pr](https://github.com/python-discord/django-simple-bulma/pull/55) for some context on how to go about doing
that).

#### CSS style

The `output_style` parameter determines the style of the resulting CSS file. It can be any of `"nested"` (default)
, `"expanded"`, `"compact"`, and `"compressed"`. It is recommended to use `"compressed"` in production as to reduce the
final file size.

#### FontAwesome

The optional `fontawesome_token` parameter allows you to specify your personal FontAwesome kit, which is necessary for
FontAwesome v6 and up. This should be set to the identifier part of your FontAwesome kit script src parameter. For
example, if your FontAwesome kit looks like this:

```html
<script src="https://kit.fontawesome.com/e761a01be3.js" crossorigin="anonymous"></script>
```

Then your `fontawesome_token` should be **e761a01be3**.

This is used by the `{% font_awesome %}` template tag to set up FontAwesome for you. If you don't specify
a `fontawesome_token`, **the template tag will still work**, but will then use an older version of FontAwesome (v5.14.0)
.


Compiling custom SCSS
------------------------

If you're writing custom SCSS for your application, `django-simple-bulma` provides a mechanism for compiling it for you.
This is provided mainly because `django-simple-bulma` may cause conflicts and issues with other tools to compile SCSS
for you.

To use this feature, please specify the `custom_scss` key when defining your `BULMA_SETTINGS`. This should be a list of
strings, containing _relative paths_ to `.scss` files to be compiled.

```python
BULMA_SETTINGS = {
  "custom_scss": [
    "css/base/base.scss",                  # This is okay
    "my_app/static/css/base/base.scss",    # This also is okay
    "C:\Users\MainDawg\my_app\static\..."  # Don't do this, though.
  ],
}
```

The default Django behavior when collecting static files is to keep the containing file structure for them when they're
copied over to the final staticfiles directory. We do the same thing, so all directories and subdirectories will still
be intact in your staticfiles folder after they've been collected.

Here's the strategy the finder uses:

* If your path contains `static/`, assume that the base path ends there and use the rest of the path as a relative path
  to the resource.
* Use whatever Finders you have enabled in your `settings.py` to search for the file using that relative path.
* If the path is found using one of these Finders, compile it to css and collect it.
* Otherwise, raise a `ValueException` asking you to double-check the filepath.

Migration Guide: v2.x to v3.0
------------------------------

**django-simple-bulma v3.0** includes significant changes to support Bulma 1.0+ and focuses on actively maintained extensions only. This is a **breaking change** that requires migration steps.

### What's Changed

- **Bulma version**: Upgraded from v0.9.4 to v1.0+
- **Extension support**: Streamlined from 18+ extensions to 2 actively maintained extensions
- **Compatibility**: All extensions are now Bulma 1.0+ compatible and actively maintained

### Removed Extensions

The following extensions have been **removed** due to being unmaintained or incompatible with Bulma 1.0+:

- `bulma-badge`
- `bulma-carousel`
- `bulma-checkradio`
- `bulma-collapsible`
- `bulma-coolcheckboxes`
- `bulma-divider`
- `bulma-megamenu`
- `bulma-pageloader`
- `bulma-pricingtable`
- `bulma-quickview`
- `bulma-ribbon`
- `bulma-slider`
- `bulma-steps`
- `bulma-switch`
- `bulma-tagsinput`
- `bulma-timeline`

### Supported Extensions (v3.0+)

Only actively maintained, Bulma 1.0+ compatible extensions are now supported:

- **[bulma-calendar](https://github.com/michael-hack/bulma-calendar)**: Calendar and datepicker components (v7.1.1+)
- **[bulma-tooltip](https://github.com/CreativeBulma/bulma-tooltip)**: Tooltip components (v1.2.0+)
- **[bulma-responsive-tables](https://github.com/justboil/bulma-responsive-tables)**: Responsive table components for mobile-friendly tables
- **[bulma-switch-control](https://github.com/justboil/bulma-switch-control)**: Switch/toggle control components
- **[bulma-radio](https://github.com/justboil/bulma-radio)**: Enhanced radio button components
- **[bulma-checkbox](https://github.com/justboil/bulma-checkbox)**: Enhanced checkbox components  
- **[bulma-upload-control](https://github.com/justboil/bulma-upload-control)**: File upload control components


## Migration Steps

### Update Your BULMA_SETTINGS

Remove any unsupported extensions from your configuration:

```python
# Before (v2.x)
BULMA_SETTINGS = {
    "extensions": [
        "bulma-collapsible",    # ❌ No longer supported
        "bulma-calendar",       # ✅ Still supported (new maintained version)
        "bulma-tooltip",        # ✅ Still supported  
        "bulma-tagsinput",      # ❌ No longer supported
        "bulma-badge",          # ❌ No longer supported
        # ... other removed extensions
    ],
    # ... other settings remain the same
}

# After (v3.0+)
BULMA_SETTINGS = {
    "extensions": [
        "bulma-calendar",          # ✅ Updated to maintained version
        "bulma-tooltip",           # ✅ Updated to maintained version
        "bulma-responsive-tables", # ✅ New JustBoil extension
        "bulma-switch-control",    # ✅ New JustBoil extension
        "bulma-radio",             # ✅ New JustBoil extension
        "bulma-checkbox",          # ✅ New JustBoil extension
        "bulma-upload-control",    # ✅ New JustBoil extension
    ],
    # ... other settings remain the same
}
```

### Alternative Solutions for Removed Extensions

If you were using removed extensions, here are specific, modern alternatives that work well with Bulma:

**For form controls (checkradio, switch, slider):**
- **Custom CSS Solutions**: Use [Pretty Checkbox](https://lokesh-coder.github.io/pretty-checkbox/) (pure CSS library) or [CSS-Tricks custom checkboxes guide](https://css-tricks.com/zero-trickery-custom-radios-and-checkboxes/)
- **Modern HTML5**: Native `<input type="range">` for sliders, styled with CSS custom properties
- **Accessibility-first**: [Modern CSS Solutions for radio buttons](https://moderncss.dev/pure-css-custom-styled-radio-buttons/) with built-in accessibility

**For carousel components:**
- **[Swiper](https://swiperjs.com/)**: Modern, performant carousel with Bulma CSS compatibility
- **[Embla Carousel](https://www.embla-carousel.com/)**: Lightweight, framework-agnostic carousel library  
- **[Glider.js](https://nickpiscitelli.github.io/Glider.js/)**: Fast, dependency-free carousel with responsive breakpoints

**For layout components (collapsible, steps, timeline):**
- **Collapsible**: Use Bulma's [`is-hidden` modifier](https://bulma.io/documentation/modifiers/display-responsive/) with custom JavaScript toggle functions
- **Steps**: Build with Bulma's [breadcrumb component](https://bulma.io/documentation/components/breadcrumb/) styling or custom flexbox layouts
- **Timeline**: CSS-only solutions using [flexbox utilities](https://bulma.io/documentation/helpers/flexbox-helpers/) and [Bulma's spacing helpers](https://bulma.io/documentation/helpers/spacing-helpers/)

**For UI elements (badge, ribbon, divider):**
- **Badge**: Use Bulma's [`tag` component](https://bulma.io/documentation/elements/tag/) or [`notification is-small`](https://bulma.io/documentation/elements/notification/) for badge-like elements
- **Ribbon**: CSS-only ribbon effects using `::before`/`::after` pseudo-elements with [Bulma colors](https://bulma.io/documentation/overview/colors/)
- **Divider**: Use [`hr` element](https://bulma.io/documentation/elements/other/#horizontal-rule) with custom CSS or [title component](https://bulma.io/documentation/elements/title/) styling

**For advanced components:**
- **Modal/Dropdown**: Use the built-in JavaScript helpers already included in django-simple-bulma or Bulma's [`modal`](https://bulma.io/documentation/components/modal/)/[`dropdown`](https://bulma.io/documentation/components/dropdown/) components
- **Pageloader**: CSS-only loading animations using Bulma's [`loader` mixin](https://bulma.io/documentation/elements/button/#loading-button) and custom positioning
- **Quickview**: Implement with Bulma's [`modal` component](https://bulma.io/documentation/components/modal/) and custom JavaScript

### Test Your Application

After updating your settings:

1. Run `python manage.py collectstatic` to rebuild your CSS
2. Test that your forms and UI components still work as expected
3. Verify that only supported extensions are being loaded
4. Check for any styling regressions

### Update Custom CSS (if needed)

If you have custom CSS that depends on removed extensions:

1. Remove any `@import` statements referencing removed extensions
2. Replace extension-specific classes with custom implementations
3. Test your styling changes across different screen sizes


Development
-----------

This project uses [UV](https://github.com/astral-sh/uv) for dependency management and development workflows. UV is a fast Python package manager that simplifies development setup.

### Setting up your development environment

1. **Install UV** (if you haven't already):
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or using pip
   pip install uv
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/python-discord/django-simple-bulma.git
   cd django-simple-bulma
   ```

3. **Install dependencies**:
   ```bash
   # Install all dependencies including dev dependencies
   uv sync --all-extras
   ```

### Pre-commit hooks

We use pre-commit hooks to ensure code quality. Install them with:

```bash
uv run pre-commit install
```

This will run our linting checks automatically before each commit.

Troubleshooting
---------------

- If you have the module `sass` installed, please note that it is incompatible with this project. There is a namespace
  conflict between `sass` and `libsass` which will make `django-simple-bulma` crash when you attempt to do
  a `collectstatic`. To solve this, just uninstall `sass` and use `libsass` instead.

If you run into any other problems with this app,
please [create an issue](https://github.com/python-discord/django-simple-bulma/issues), and I will be happy to help
you with it. You can also find me on Discord as `lemon#0001` at https://discord.gg/python.
