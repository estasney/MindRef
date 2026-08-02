import glob
import hashlib
from os.path import exists, join
from pathlib import Path

import sh
from pythonforandroid.archs import Arch
from pythonforandroid.build import Context
from pythonforandroid.logger import info, info_main, shprint
from pythonforandroid.recipe import PyProjectRecipe
from pythonforandroid.util import rmdir
from typing import ClassVar


def source_digest(build_dir: Path, entries: list[str]) -> str:
    """Digest the copied source set by path and content, so equal trees
    produce equal digests regardless of file timestamps."""
    digest = hashlib.sha256()
    for entry in entries:
        entry_path = build_dir / entry
        if entry_path.is_file():
            digest.update(entry.encode())
            digest.update(entry_path.read_bytes())
            continue
        for file_path in sorted(p for p in entry_path.rglob("*") if p.is_file()):
            digest.update(str(file_path.relative_to(build_dir)).encode())
            digest.update(file_path.read_bytes())
    return digest.hexdigest()


class MindRefAndroidRecipe(PyProjectRecipe):
    """Builds MindRef from a copy of the working tree.

    The extension module is compiled from the committed ``ext.c``, so Cython is
    not needed at build time. Depending on p4a's ``cython`` recipe would pull in
    a cross-compiled Cython 0.29.36, which cannot build against Python 3.14.
    """

    ctx: ClassVar[Context]

    name = "mindref_android"
    depends: ClassVar[list[str]] = ["setuptools"]
    site_packages_name = "mindref"
    project_root = Path(__file__).parent.parent.parent
    source_entries: ClassVar[list[str]] = ["src", "pyproject.toml", "README.md"]

    def source_stamp_path(self, arch_name: str) -> Path:
        return Path(self.get_build_container_dir(arch_name)) / "source.sha256"

    def current_source_digest(self, arch_name: str) -> str:
        return source_digest(Path(self.get_build_dir(arch_name)), self.source_entries)

    def should_build(self, arch: "Arch") -> bool:
        if not self.ctx.has_package(self.folder_name, arch):
            info(f"{self.folder_name} is not in site-packages")
            return True
        stamp_path = self.source_stamp_path(arch.arch)
        if not stamp_path.exists():
            info("No source digest recorded from a previous build")
            return True
        if stamp_path.read_text() != self.current_source_digest(arch.arch):
            info("Source files changed since the previous build")
            return True
        info("Source files unchanged since the previous build")
        return False

    def build_arch(self, arch: "Arch") -> None:
        digest = self.current_source_digest(arch.arch)
        super().build_arch(arch)
        self.source_stamp_path(arch.arch).write_text(digest)

    def check_prebuilt(self, arch: "Arch", msg: str = "") -> bool:
        """MindRef is built from the local repository and never published, so
        querying an index for a prebuilt wheel only produces a failed lookup."""
        return False

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
        """Syncs the working tree into the build dir. We should not super()
        this method, because it will try to download."""
        info_main(f"Unpacking {self.name} for {arch}")
        build_dir = Path(self.get_build_dir(arch))
        if (build_dir / ".git").exists():
            info(f"Removing git clone left by the previous recipe at {build_dir}")
            rmdir(str(build_dir))
        build_dir.mkdir(parents=True, exist_ok=True)
        info(f"Syncing working tree {self.project_root} to {build_dir}")
        shprint(
            sh.rsync,
            "-a",
            "--delete",
            "--exclude",
            "__pycache__/",
            "--exclude",
            "*.pyc",
            f"{self.project_root / 'src'}/",
            str(build_dir / "src"),
        )
        for file_name in ("pyproject.toml", "README.md"):
            shprint(sh.cp, str(self.project_root / file_name), str(build_dir))
        for stale_name in ("setup.py", "MANIFEST.in"):
            stale_file = build_dir / stale_name
            if stale_file.exists():
                info(f"Removing {stale_file} left by the previous recipe")
                stale_file.unlink()
        stale_wheel_dir = build_dir / "dist"
        if stale_wheel_dir.exists():
            info(f"Removing stale wheels at {stale_wheel_dir}")
            rmdir(str(stale_wheel_dir))


recipe = MindRefAndroidRecipe()
