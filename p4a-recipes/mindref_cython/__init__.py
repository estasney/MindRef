import os
from pathlib import Path

import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import CythonRecipe, IncludedFilesBehaviour
import shutil


class MindRefCythonRecipe(IncludedFilesBehaviour, CythonRecipe):
    """Custom recipe to have our cython files compiled for multi-arch"""

    name = "mindref_cython"
    cythonize = True
    depends = ["setuptools"]
    src_filename = "src"
    python_depends = []
    repo_path = Path(__file__).parent.parent.parent / "mindref"

    def _get_source_files(self):
        """
        In mindref repo, get a listing of all .pxd and .pyx files
        """

        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".pxd") or file.endswith(".pyx"):
                    yield Path(os.path.join(root, file))

    def prepare_build_dir(self, arch):
        build_dir = self.get_build_dir(arch)
        shprint(sh.rm, "-rf", build_dir)
        shprint(
            sh.cp,
            "-a",
            os.path.join(self.get_recipe_dir(), self.src_filename),
            build_dir,
        )
        # Copy our just fetched files to the build dir
        # Our target files should be nested under mindref_cython
        src_files = self._get_source_files()
        for src_file in src_files:
            dest_file = Path(build_dir) / self.name / src_file.name
            print(f"Copying {src_file} to {dest_file}")
            shprint(sh.cp, str(src_file), str(dest_file))


recipe = MindRefCythonRecipe()
