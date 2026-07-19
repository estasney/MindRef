"""Local override of python-for-android's built-in ``android`` recipe.

The ``android`` Python module this recipe compiles ships only a ``setup.py``,
which imports Cython without a ``pyproject.toml`` declaring it as a build
requirement. Building its wheel under PEP 517 isolation therefore fails with
``ModuleNotFoundError: No module named 'Cython'``. Disabling isolation builds
against hostpython instead, where the recipe's own
``hostpython_prerequisites`` already installed a version-pinned Cython.
"""

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import ClassVar

import pythonforandroid.recipes


def upstream_recipe_dir() -> Path:
    """Locate the built-in ``android`` recipe shipped with python-for-android."""
    recipes_package = pythonforandroid.recipes.__file__
    if recipes_package is None:
        raise RuntimeError("python-for-android recipes package has no file location")
    return Path(recipes_package).parent / "android"


def load_upstream_recipe_module() -> ModuleType:
    """Import the built-in recipe by file path.

    Local recipes are imported under the module name
    ``pythonforandroid.recipes.android`` -- the same name as the built-in one --
    so importing the original by module path would resolve back to this module.
    """
    recipe_file = upstream_recipe_dir() / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        "mindref_upstream_android_recipe", recipe_file
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load built-in android recipe from {recipe_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NoBuildIsolationAndroidRecipe(load_upstream_recipe_module().AndroidRecipe):
    extra_build_args: ClassVar[list[str]] = ["--no-isolation"]

    def get_recipe_dir(self) -> str:
        """Keep sourcing files from upstream rather than this override's directory."""
        return str(upstream_recipe_dir())


recipe = NoBuildIsolationAndroidRecipe()
