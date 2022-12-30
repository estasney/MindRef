#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import os
from distutils.extension import Extension

from setuptools import find_packages, setup
from Cython.Build import cythonize

# Package meta-data
NAME = "MindRef"
DESCRIPTION = "Cross-Platform Application for maintaining Markdown formatted notes"
URL = "https://github.com/estasney/MindRef"
EMAIL = "estasney@users.noreply.github.com"
AUTHOR = "Eric Stasney"
REQUIRES_PYTHON = ">=3.10"

# What packages are required for this module to be executed?
REQUIRED = [
    "Cython==0.29.32",
    "Kivy==2.1.0",
    "mistune==2.0.4",
    "Pillow==9.3.0",
    "Pygments==2.13.0",
    "python-dotenv==0.21.0",
    "toolz==0.12.0",
]

EXTRAS = {
    "dev": ["pre-commit", "pytest", "PyYAML", "click"],
    "android": ["python-for-android", "pyjnius"],
}

here = os.path.abspath(os.path.dirname(__file__))
long_description = DESCRIPTION

about = {}
with open(os.path.join(here, "__version__.py"), "r") as fp:
    exec(fp.read(), about)

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
    extras_require=EXTRAS,
    include_package_data=True,
    data_files=[
        (
            "data",
            [
                "mindref/static/icons/*",
                "mindref/static/textures/*",
            ],
        )
    ],
    license="LGPLv3+",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    ],
    ext_modules=cythonize(
        [
            Extension(
                "mindref.utils.calculation",
                ["mindref/utils/calculation.pyx"],
            ),
            Extension("mindref.utils.index", ["mindref/utils/index.pyx"]),
        ],
        compiler_directives={"language_level": 3},
    ),
)
