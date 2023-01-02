from distutils.core import setup, Extension

from setuptools import find_packages

modules = [
    Extension("calculation", ["mindref_cython/calculation.c"]),
    Extension("index", ["mindref_cython/index.c"]),
    Extension("scrolling_c", ["mindref_cython/scrolling_c.c"]),
]

setup(
    name="mindref_cython", version="1.0", packages=find_packages(), ext_modules=modules
)
