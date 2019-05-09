django-simple-bulma
===================
[![Build Status](https://dev.azure.com/python-discord/Python%20Discord/_apis/build/status/Django%20Simple%20Bulma?branchName=master)](https://dev.azure.com/python-discord/Python%20Discord/_build/latest?definitionId=7?branchName=master)
[![Discord](https://discordapp.com/api/guilds/267624335836053506/embed.png)](https://discord.gg/2B963hn)

`django-simple-bulma` is a Django application that makes [Bulma](https://bulma.io) and [Bulma-Extensions](https://wikiki.github.io/) available to use in your Django project with as little setup as possible. The goal of this project is to make it as easy as possible to use Bulma with Django.

This project currently uses **Bulma v0.7.2**, **Bulma-Extensions v4.0.0**, and **FontAwesome v5.6.3**. If you want features that are only available in newer versions of these frameworks, please [create an issue](https://github.com/python-discord/django-simple-bulma/issues), and we will be happy to update it.

Installation
------------
To get `django-simple-bulma`, up and running for your Django project, follow these simple steps:
- Install it from PyPI with `pip install django-simple-bulma` (or add it to your [Pipfile](https://pipenv.readthedocs.io/en/latest/))
- In your Django projects `settings.py` file:
  - Add `django_simple_bulma` to your `INSTALLED_APPS`
    ```python
    INSTALLED_APPS = [
      #...
      'django_simple_bulma',
      #...
    ]
    ``` 
  - Add `django_simple_bulma.finders.SimpleBulmaFinder` to your `STATICFILES_FINDERS`. This normally holds two default handlers that you will probably want to keep, so unless you have any other custom Finders, it should look like this:
    ```python
    STATICFILES_FINDERS = [
      # First add the two default Finders, since this will overwrite the default.
      'django.contrib.staticfiles.finders.FileSystemFinder',
      'django.contrib.staticfiles.finders.AppDirectoriesFinder',
  
      # Now add our custom SimpleBulma one.
      'django_simple_bulma.finders.SimpleBulmaFinder',
    ]
    ```
- Run `python manage.py collectstatic` command in order to build Bulma and move it to your `staticfiles` folder. Please note that you will need to use this command every time you make a change to the configuration, as this is the only way to rebuild the Bulma css file. If you are not using `collectstatic`, [read up on it](https://stackoverflow.com/questions/34586114/whats-the-point-of-djangos-collectstatic) and [start using it](https://docs.djangoproject.com/en/2.1/ref/contrib/staticfiles/). 

  This app works fine with [Whitenoise](http://whitenoise.evans.io/en/stable/), which is a great way to serve static files without needing to mess with your webserver.
  
`django-simple-bulma` should now be working! In order to import it into your template, first load the app with `{% load django_simple_bulma %}`, and then use the `{% bulma %}` template tag. If you're planning on using icons, you should also import FontAwesome by using `{% font_awesome %}`.
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
Bulma looks nice by default, but most users will want to customize its look and feel. For this, we've provided a super simple way to change the [Bulma variables](https://bulma.io/documentation/customize/variables/) and to choose which [Bulma extensions](https://wikiki.github.io/) you want to load into your project.

In order to do this, we'll simply create a dictionary inside your `settings.py` called `BULMA_SETTINGS`, and configure it there. Here's an example of what that looks like:
```python
# Custom settings for django-simple-bulma
BULMA_SETTINGS = {
    "extensions": [
        "bulma-accordion",
        "bulma-calendar",
    ],
    "variables": {
        "primary": "#000000",
        "size-1": "6rem",
    }
}
```

You may here define any variable found on the [Bulma variables](https://bulma.io/documentation/customize/variables/) page, and you may use any valid SASS or CSS as the value. For example, `hsl(217, 71%, 53%)` would be a valid value for a color variable, as would `#ffff00`. Please note that any syntactically incorrect values may prevent Bulma from building correctly, so be careful what you add here unless you know exactly what you're doing.

If the `extensions` key is not found, it will default to loading **all extensions**. If you don't want any extensions, simply set it to an empty list.

Additional scripts
------------------
For your convenience, we also give you the option to add other quality of life improvements to your Bulma app. If you are not specifying any extensions in `BULMA_SETTINGS`, these will all be loaded by default. If you are, you may want to add these as well if they sound useful to you.

* `bulma-fileupload` will handle displaying the filename in your [file upload inputs](https://bulma.io/documentation/form/file/).
* `bulma-navbar-burger` will hook up your `navbar-burger`s and `navbar-menu`s automatically, to provide a toggle for mobile users. We use a slightly updated version of [the example from Bulma's documentation](https://bulma.io/documentation/components/navbar/#navbarJsExample) - simply add a `data-target` attribute to your `navbar-burger` that refers to the `id` of the `navbar-menu` that should be expanded and collapsed by the button.
* `bulma-notifications` will allow you to close [notifications](https://bulma.io/documentation/elements/notification/) by clicking on the X button.

Additional functionality
------------------------

If you're writing custom SCSS for your application, `django-simple-bulma` does provide a very basic mechanism for compiling
it for you. This is provided because, currently, `django-simple-bulma` will cause issues with current Django apps that exist
to compile SCSS for you.

To use this feature, please specify the `custom_css` key when defining your `BULMA_SETTINGS`. This should be a list
of strings, containing relative paths to `.scss` files to be compiled.

```python
BULMA_SETTINGS = {
    "custom_scss": [
        "myapp/static/css/base/base.scss"
    ],
}
```

**Please note**: The default Django behavior when collecting static files is to keep the containing file structure for
them when they're copied over to the final static files directory. We attempt to do the same thing by parsing the given
path to your `.scss` file, using the following strategy:

* If a containing path exists in the `STATICFILES_DIRS` setting, assume that this is the base path to use, and the
  directory structure below it will be used to contain the resulting `.css` file
* Otherwise, if the path contains `static/`, assume that the base path ends there and use the rest of the path
  below it to contain the resulting `.css` file.
 
If both of these strategies fail to figure out what base path to use, an exception will be raised.

Troubleshooting
---------------

- If you have the module `sass` installed, please note that it is incompatible with this project. There is a namespace conflict between `sass` and `libsass` which will make `django-simple-bulma` crash when you attempt to do a `collectstatic`. To solve this, just uninstall `sass` and use `libsass` instead. 

If you run into any other problems with this app, please [create an issue](https://github.com/python-discord/django-simple-bulma/issues), and we will be happy to help you with it. Alternatively, head over to our discord server at https://discord.gg/python and we'll help you figure it out over chat.
