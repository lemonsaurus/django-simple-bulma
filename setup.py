"""
This file is used to install this package via the pip tool.

It keeps track of versioning, as well as dependencies and
what versions of python or django we support.
"""

from setuptools import find_packages, setup

setup(
    name="django-simple-bulma",
    version="1.0.1",
    description="Django application to add the Bulma CSS framework and its extensions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Python Discord",
    author_email="staff@pythondiscord.com",
    url="http://pypi.python.org/pypi/django-simple-bulma",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "Django>=2.0",
        "libsass",
    ],
    extras_require={
        "dev": [
            "flake8",
            "flake8-bugbear",
            "flake8-docstrings",
            "flake8-import-order",
            "flake8-quotes",
            "flake8-tidy-imports",
            "flake8-todo",
            "flake8-type-annotations",
            "flake8-string-format",
            "pdoc",
            "PyGithub",
            "wheel",
        ]
    },
    include_package_data=True,
    zip_safe=False
)
