from pythonforandroid.recipe import CythonRecipe, IncludedFilesBehaviour


class MindRefRecipe(IncludedFilesBehaviour, CythonRecipe):
    """Custom recipe to have our cython files compiled for multi-arch"""

    name = "utils"
    cythonize = True
    depends = ["setuptools"]
    src_filename = "src"
    python_depends = []


recipe = MindRefRecipe()
