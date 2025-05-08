django-simple-bulma
===================
`django-simple-bulma` is a Django application that makes [Bulma](https://bulma.io)
and [Bulma-Extensions](https://wikiki.github.io/) available to use in your Django project with as little setup as
possible. The goal of this project is to make it as easy as possible to use Bulma with Django.

This project currently uses **Bulma v0.9.4**, and is automatically updated with every new release. If a new version has
come out with features you'd like to make use of,
please [create an issue](https://github.com/python-discord/django-simple-bulma/issues), and we will be happy to make a
release to update it.

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
    "bulma-collapsible",
    "bulma-calendar",
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

We currently support these extensions:

- [bulma-badge](https://github.com/CreativeBulma/bulma-badge/)
- [bulma-calendar](https://github.com/Wikiki/bulma-calendar)
- [bulma-carousel](https://github.com/Wikiki/bulma-carousel)
- [bulma-collapsible](https://github.com/CreativeBulma/bulma-collapsible)
- [bulma-checkradio](https://github.com/Wikiki/bulma-checkradio)
- [bulma-divider](https://github.com/CreativeBulma/bulma-divider)
- [bulma-megamenu](https://github.com/hunzaboy/bulma-megamenu)
- [bulma-pageloader](https://github.com/Wikiki/bulma-pageloader)
- [bulma-pricingtable](https://github.com/Wikiki/bulma-pricingtable)
- [bulma-quickview](https://github.com/Wikiki/bulma-quickview)
- [bulma-ribbon](https://github.com/Wikiki/bulma-ribbon)
- [bulma-slider](https://github.com/Wikiki/bulma-slider)
- [bulma-steps](https://github.com/Wikiki/bulma-steps)
- [bulma-switch](https://github.com/Wikiki/bulma-switch)
- [bulma-tagsinput](https://github.com/CreativeBulma/bulma-tagsinput)
- [bulma-timeline](https://github.com/Wikiki/bulma-timeline)
- [bulma-tooltip](https://github.com/CreativeBulma/bulma-tooltip)
- [bulma-coolcheckboxes (Cool-Checkboxes-for-Bulma.io)](https://github.com/hunzaboy/Cool-Checkboxes-for-Bulma.io)

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

Additional scripts
------------------
For your convenience, we also give you the option to add other quality of life improvements to your Bulma app. You may
want to add these as well if they sound useful to you.

* `bulma-fileupload` will handle displaying the filename in
  your [file upload inputs](https://bulma.io/documentation/form/file/).
* `bulma-navbar-burger` will hook up your `navbar-burger`s and `navbar-menu`s automatically, to provide a toggle for
  mobile users. We use a slightly updated version
  of [the example from Bulma's documentation](https://bulma.io/documentation/components/navbar/#navbarJsExample) -
  simply add a `data-target` attribute to your `navbar-burger` that refers to the `id` of the `navbar-menu` that should
  be expanded and collapsed by the button.
* `bulma-notifications` will allow you to close [notifications](https://bulma.io/documentation/elements/notification/)
  by clicking on the X button.
* `bulma-dropdown` will open/close dropdowns using the `is-active` class. It mimics how the dropdowns function on
  the [documentation page](https://bulma.io/documentation/components/dropdown/#hoverable-or-toggable).
* `bulma-modal` will handle opening and closing modals. Just assign the `modal-button` class to a `<button>`, and make
  sure it has a `data-target` attribute that matches the `id` of the modal that you want to open.
  See [the example code from Bulma's documentation](https://bulma.io/documentation/components/modal/) for modal element
  code.

Compiling custom SCSS
------------------------

If you're writing custom SCSS for your application, `django-simple-bulma` provides a mechanism for compiling it for you.
This is provided mainly because `django-simple-bulma` may cause conflicts and issues with other tools to compile SCSS
for you.

To use this feature, please specify the `custom_css` key when defining your `BULMA_SETTINGS`. This should be a list of
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

Troubleshooting
---------------

- If you have the module `sass` installed, please note that it is incompatible with this project. There is a namespace
  conflict between `sass` and `libsass` which will make `django-simple-bulma` crash when you attempt to do
  a `collectstatic`. To solve this, just uninstall `sass` and use `libsass` instead.

If you run into any other problems with this app,
please [create an issue](https://github.com/python-discord/django-simple-bulma/issues), and I'll will be happy to help
you with it. You can also find me on Discord as `lemon#0001` at https://discord.gg/python.
