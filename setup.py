"""
This file is used to install this package via the pip tool.

It keeps track of versioning, as well as dependencies and
what versions of python or django we support.
"""

from setuptools import find_packages, setup

setup(
    name="django-simple-bulma",
    version="1.2.0",
    description="Django application to add the Bulma CSS framework and its extensions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Python Discord",
    author_email="staff@pythondiscord.com",
    url="https://github.com/python-discord/django-simple-bulma",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "Django>=2.0",
        "libsass~=0.19",
    ],
    extras_require={
        "dev": [
            "flake8~=3.7",
            "flake8-bugbear~=19.8",
            "flake8-import-order~=0.18",
            "flake8-tidy-imports~=2.0",
            "flake8-todo~=0.7",
            "flake8-string-format~=0.2",
            "pdoc~=0.3",
            "pre-commit~=1.18",
            "PyGithub~=1.43",
            "wheel~=0.33",
        ]
    },
    include_package_data=True,
    zip_safe=False
)
