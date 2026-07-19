import glob
from os.path import join, exists
from pathlib import Path

import sh
from pythonforandroid.archs import Arch
from pythonforandroid.build import Context
from pythonforandroid.logger import info, info_main, shprint
from pythonforandroid.recipe import PyProjectRecipe
from pythonforandroid.util import rmdir
from typing import ClassVar


class MindRefAndroidRecipe(PyProjectRecipe):
    """Builds MindRef from a clone of the local repository.

    The extension module is compiled from the committed ``ext.c``, so Cython is
    not needed at build time. Depending on p4a's ``cython`` recipe would pull in
    a cross-compiled Cython 0.29.36, which cannot build against Python 3.14.
    """

    ctx: ClassVar[Context]

    name = "mindref_android"
    depends: ClassVar[list[str]] = ["setuptools"]
    site_packages_name = "mindref"
    repo_path = Path(__file__).parent.parent.parent / ".git"
    branch_name = "dev"

    def should_build(self, arch):
        return True

    def clean_build(self, arch=None):
        if arch is None:
            base_dir = join(self.ctx.build_dir, "other_builds", self.name)
        else:
            base_dir = self.get_build_container_dir(arch)

        shprint(sh.rm, "-rf", base_dir)
        name = self.folder_name
        python_install_dirs = glob.glob(join(self.ctx.python_installs_dir, "*"))
        for python_install in python_install_dirs:
            site_packages_dir = glob.glob(
                join(python_install, "lib", "python*", "site-packages")
            )
            if site_packages_dir:
                build_dir = join(site_packages_dir[0], name)
                if exists(build_dir):
                    info(f"Deleted {build_dir}")
                    rmdir(build_dir)

    def prepare_build_dir(self, arch):
        """
        This is where we will clone the MindRef to the build dir.
        We should not super() this method, because it will try to download
        """
        info_main(f"Unpacking {self.name} for {arch}")
        build_dir = Path(self.get_build_container_dir(arch)) / self.name
        build_dir.mkdir(parents=True, exist_ok=True)
        info(f"Cloning MindRef to build dir {build_dir}")
        info(f"Repo path: {self.repo_path!s}")
        shprint(
            sh.git,
            "clone",
            "--branch",
            self.branch_name,
            "--single-branch",
            "--depth=1",
            str(self.repo_path),
            str(build_dir),
        )
        # Copy our setup.py file to the build dir
        info(f"Copying setup.py to {build_dir}")
        setup_py_path = Path(__file__).parent / "setup.py"
        shprint(sh.cp, str(setup_py_path), str(build_dir))

        info(f"Copying MANIFEST.in to {build_dir}")
        manifest_in_path = Path(__file__).parent / "MANIFEST.in"
        shprint(sh.cp, str(manifest_in_path), str(build_dir))

        # Remove the pyproject.toml file
        pyproject_toml_path = build_dir / "pyproject.toml"
        if pyproject_toml_path.exists():
            info(f"Removing {pyproject_toml_path}")
            shprint(sh.rm, str(pyproject_toml_path))


recipe = MindRefAndroidRecipe()
