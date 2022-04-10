#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import os

from setuptools import find_packages, setup

# Package meta-data
NAME = "kvnoteafly"
DESCRIPTION = "Kivy Note App"
URL = "https://github.com/estasney/KVNoteAFly"
EMAIL = "estasney@users.noreply.github.com"
AUTHOR = "Eric Stasney"
REQUIRES_PYTHON = ">=3.9.0"
VERSION = "0.0.1"

# What packages are required for this module to be executed?
REQUIRED = [
    "python-dotenv",
    "sqlalchemy",
    "toolz",
    "Kivy[base]",
    "Pygments",
    "Pillow",
    "requests",
    "sqlalchemy-utils",
    "click",
    "pyperclip",
    "marko[codehilite]",
]

here = os.path.abspath(os.path.dirname(__file__))
long_description = DESCRIPTION

about = {}
about["__version__"] = VERSION

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=("tests",)),
    install_requires=REQUIRED,
    include_package_data=True,
    data_files=[
        (
            "data",
            ["kvnoteafly/db/noteafly.db", "kvnoteafly/static/category_icons/*"],
        )
    ],
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
