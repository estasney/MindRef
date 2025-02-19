from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from operator import itemgetter
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, NamedTuple, NewType

import PIL.Image
from kivy.atlas import Atlas as KivyAtlas

from mindref.lib.adapters.atlas import AbstractAtlasRepository
from mindref.lib.utils import EnvironContext, LazyLoaded

if TYPE_CHECKING:
    from collections.abc import Sequence


class AtlasItem(NamedTuple):
    name: str
    path: Path


X = NewType("X", int)
Y = NewType("Y", int)
W = NewType("W", int)
H = NewType("H", int)
ImgPos = NewType("ImgPos", tuple[X, Y, W, H])
AtlasFileData = dict[str, dict[str, ImgPos]]


class AtlasService(AbstractAtlasRepository):
    """
    Manages Atlases
    - Storage Location
    - Inserting and Removing
    - Provides path for kivy usage
    """

    builtin_atlases: ClassVar[set[str]] = {"icons", "textures"}
    atlases: LazyLoaded[list[AtlasItem]] = LazyLoaded()
    _storage_path: Path | None
    _instance = None

    def __init__(self, storage_path: Path | str | None = None):
        self.storage_path = storage_path
        self._atlases = None

    def __contains__(self, item):
        """
        Determine if an image belongs in one of AtlasService's atlases

        This should be passed with the form '{atlas_name}.{image_name}'
        """
        if "." not in item:
            raise ValueError(f"Expected {item} to be of form atlas_name.image_name")
        atlas_name, image_name = item.split(".")
        atlas_data = self._read_atlas(atlas_name)
        image_names = {name for name_grp in atlas_data.values() for name in name_grp}
        return image_name in image_names

    @property
    def storage_path(self) -> Path:
        if self._storage_path is None:
            raise AttributeError("Storage Path not set")
        return self._storage_path

    @storage_path.setter
    def storage_path(self, value: Path | str):
        self._storage_path = Path(value)

    @atlases
    def _discover_atlases(self) -> list[AtlasItem]:
        """
        Discover all atlases in storage path
        """
        atlas: list[AtlasItem] = []
        for item in self.storage_path.iterdir():
            if item.is_dir() and (af := next(item.glob("*.atlas"), None)):
                atlas.append(AtlasItem(item.stem, af))
        missed = self.builtin_atlases - {name for name, _ in atlas}
        if not missed:
            return atlas
        for missed_atlas in missed:
            fp = (
                self.storage_path / missed_atlas / missed_atlas.replace("_", "-")
            ).with_suffix(".atlas")
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.touch()
            fp.write_text("{}")
            atlas.append(AtlasItem(missed_atlas, fp))
        return atlas

    def _match_atlas(self, atlas_name: str) -> AtlasItem:
        try:
            return next(atlas for atlas in self.atlases if atlas.name == atlas_name)
        except StopIteration as e:
            raise KeyError(f"{atlas_name} does not exist") from e

    def _read_atlas(self, atlas_name: str) -> AtlasFileData:
        matched_item = self._match_atlas(atlas_name)
        with matched_item.path.open(mode="r", encoding="utf-8") as fp:
            return json.load(fp)

    def _store_atlas(self, atlas_name, data):
        matched_item = self._match_atlas(atlas_name)
        with matched_item.path.open(mode="w+", encoding="utf-8") as fp:
            json.dump(data, fp)

    def _atlas_path(self, atlas_name: str) -> Path:
        matched_item = self._match_atlas(atlas_name)
        return matched_item.path.parent

    def save_to_atlas(
        self,
        images: Sequence[Path | str],
        image_names: Sequence[str],
        atlas_name: str,
        atlas_size: tuple[int, int] | None = None,
        padding: int = 2,
    ):
        """
        Lazy implementation that will create an n+1 atlas image large enough to contain the passed images.

        Parameters
        ----------
        padding
        image_names
        images
        atlas_name
        atlas_size
            Optional, if not passed, will be inferred from existing atlas.
            If passed, expects to be of form (width, height)
        padding
            Defaults to 2

        Returns
        -------

        """

        def get_width(x: ImgPos):
            return sum(itemgetter(0, 2)(x)) + padding

        def get_height(x: ImgPos):
            return sum(itemgetter(1, 3)(x)) + padding

        def get_max_dimension(data: AtlasFileData):
            w_max, h_max = 0, 0
            for _, img_names in data.items():
                w_max = max(w_max, *(get_width(img_names[k]) for k in img_names))
                h_max = max(h_max, *(get_height(img_names[k]) for k in img_names))
            return w_max, h_max

        def get_last_image(data: AtlasFileData) -> int:
            """
            We know atlas images follow a pattern of `n.png`. Find the last `n` so we can increment
            """
            pattern = re.compile(r"(\d+)(?=.png)")
            atlas_image_names = ",".join(data.keys())
            atlas_image_numbers = (int(x) for x in pattern.findall(atlas_image_names))
            try:
                return max(atlas_image_numbers)
            except ValueError:
                return -1

        def ensure_name_integrity(data: AtlasFileData) -> bool:
            img_name_set = set(image_names)
            img_names = {
                name for name_grp in (v for v in data.values()) for name in name_grp
            }
            matched = img_names & img_name_set
            if matched:
                raise KeyError(f"{', '.join(matched)} are already preset in the atlas!")
            return True

        atlas_data = self._read_atlas(atlas_name)
        ensure_name_integrity(atlas_data)
        if not atlas_size:
            atlas_w, atlas_h = get_max_dimension(atlas_data)
        else:
            atlas_w, atlas_h = atlas_size

        temp_dir_container = tempfile.TemporaryDirectory()
        temp_dir_atlas = Path(temp_dir_container.name) / "kv_temp_atlas"

        with EnvironContext({"KIVY_NO_ARGS": "1"}):
            out_name, meta = KivyAtlas.create(
                os.fspath(temp_dir_atlas), images, (atlas_w, atlas_w)
            )

        # Now set about appending these atlas images
        atlas_n_start = get_last_image(atlas_data) + 1

        def sort_atlas_imgs(p: Path):
            return int(p.stem.rsplit("-")[-1])

        atlas_img_dst_folder = self._atlas_path(atlas_name)

        img_files = (f for f in Path(temp_dir_container.name).iterdir() if f.is_file())
        img_files = (f for f in img_files if f.suffix in {".png", ".jpg", ".jpeg"})
        for i, atlas_img in enumerate(sorted(img_files, key=sort_atlas_imgs)):
            atlas_img_name = f"{atlas_name}-{atlas_n_start + i}.png".replace("_", "-")
            dst = (atlas_img_dst_folder / atlas_img_name).with_suffix(".png")
            # Enforce lower casing
            atlas_data.update(
                {
                    atlas_img_name: {
                        k.lower(): v for k, v in meta[atlas_img.name].items()
                    }
                }
            )
            shutil.move(atlas_img, dst)

        temp_dir_container.cleanup()

        self._store_atlas(atlas_name, atlas_data)

    def get_from_atlas(self, name: str, atlas_name: str) -> "PIL.Image.Image":
        """
        Retrieve an image by name and atlas name
        Parameters
        ----------
        name
        atlas_name

        Returns
        -------

        """
        atlas_data = self._read_atlas(atlas_name)
        matched_atlas_img, matched_img = self._match_atlas_member(
            atlas_data, atlas_name, name
        )

        matched_img_size = matched_img[1]
        atlas_path = self._atlas_path(atlas_name)
        atlas_img_path = atlas_path / matched_atlas_img
        img_obj = PIL.Image.open(atlas_img_path)
        x, y, w, h = matched_img_size
        return img_obj.crop((x, (img_obj.height - h - y), x + w, y + h))

    def _match_atlas_member(
        self, atlas_data: AtlasFileData, atlas_name: str, name: str
    ) -> tuple[str, ImgPos]:
        """Find an atlas member"""
        for atlas_img, members in atlas_data.items():
            matched_img = next((members[img] for img in members if img == name), None)
            if matched_img:
                return atlas_img, matched_img

        raise KeyError(f"{name} not found in atlas {atlas_name}")

    def uri_for(self, name: str, atlas_name: str):
        matched = self._match_atlas(atlas_name)
        return f"atlas://{matched.path.with_suffix('')}/{name}"
