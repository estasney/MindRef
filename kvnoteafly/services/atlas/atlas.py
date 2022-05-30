from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import tempfile
from operator import itemgetter
from pathlib import Path
from typing import NamedTuple, NewType, Optional, Sequence, Union

from kivy import Logger

from utils.registry import app_registry
import PIL.Image
from kivy.atlas import Atlas as KivyAtlas

from services.atlas import AtlasServiceProtocol
from services.utils import LazyLoaded
from utils import EnvironContext
from .utils import read_img_sizes

ImgParamType = Union[str, Path, PIL.Image.Image]


class AtlasItem(NamedTuple):
    name: str
    path: Path


X = NewType("X", int)
Y = NewType("Y", int)
W = NewType("W", int)
H = NewType("H", int)

ImgPos = NewType("ImgPos", tuple[X, Y, W, H])
AtlasFileData = dict[str, dict[str, ImgPos]]


class AtlasService(AtlasServiceProtocol):
    """
    Manages Atlases
    - Storage Location
    - Inserting and Removing
    - Provides path for kivy usage
    """

    builtin_atlases = {"button_bar", "category_img", "keys", "textures"}
    atlases: list[AtlasItem] = LazyLoaded()
    _storage_path: Optional[Path]
    _instance = None

    def __init__(self, storage_path: Optional[Path | str] = None):
        self.storage_path = storage_path
        self._atlases = None
        app_registry.category_images(self.category_image_listener)

    def __contains__(self, item):
        """
        Determine if an image belongs in one of AtlasService's atlases

        This should be passed with the form '{atlas_name}.{image_name}'
        """
        if "." not in item:
            raise ValueError(f"Expected {item} to be of form atlas_name.image_name")
        atlas_name, image_name = item.split(".")
        atlas_data = self._read_atlas(atlas_name)
        image_names = set(name for name_grp in atlas_data.values() for name in name_grp)
        return image_name in image_names

    @property
    def storage_path(self):
        if not self._storage_path:
            raise AttributeError("Storage Path not set")
        return self._storage_path

    @storage_path.setter
    def storage_path(self, value: Path | str):
        self._storage_path = Path(value)

    @atlases
    def _discover_atlases(self):
        atlas = []
        for item in self.storage_path.iterdir():
            if item.is_dir():
                if af := next(item.glob(f"*.atlas"), None):
                    atlas.append(AtlasItem(item.stem, af))
        missed = self.builtin_atlases - set((name for name, _ in atlas))
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

    def _match_atlas(self, atlas_name: str):
        try:
            matched = next(atlas for atlas in self.atlases if atlas.name == atlas_name)
            return matched
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
        atlas_size: Optional[tuple[int, int]] = None,
        padding=2,
    ):
        """
        Lazy implementation that will create a n+1 atlas image large enough to contain the passed images.

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
            for img, img_names in data.items():
                w_max = max(
                    w_max, max((get_width(img_names[k])) for k in img_names.keys())
                )
                h_max = max(
                    h_max, max((get_height(img_names[k])) for k in img_names.keys())
                )
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
            img_names = set(
                (name for name_grp in (v for v in data.values()) for name in name_grp)
            )
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

        with EnvironContext(dict(KIVY_NO_ARGS="1")):
            out_name, meta = KivyAtlas.create(
                os.fspath(temp_dir_atlas), images, (atlas_w, atlas_w)
            )

        # Now set about appending these atlas images
        atlas_n_start = get_last_image(atlas_data) + 1

        def sort_atlas_imgs(p: Path):
            return int(p.stem.rsplit("-")[-1])

        atlas_img_dst_folder = self._atlas_path(atlas_name)
        for i, atlas_img in enumerate(
            sorted(Path(temp_dir_container.name).glob("*.png"), key=sort_atlas_imgs)
        ):
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

    def get_from_atlas(self, name: str, atlas_name: str) -> PIL.Image.Image:
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
        matched_img = None
        matched_atlas_img = None
        for atlas_img, members in atlas_data.items():
            matched_img = next(
                ((img, members[img]) for img in members if img == name), None
            )
            if matched_img:
                matched_atlas_img = atlas_img
                break
        if not matched_img:
            raise KeyError(f"{name} not found in atlas {atlas_name}")

        matched_img_size = matched_img[1]
        atlas_path = self._atlas_path(atlas_name)
        atlas_img_path = atlas_path / matched_atlas_img
        img_obj = PIL.Image.open(atlas_img_path)
        x, y, w, h = matched_img_size
        cropped_im = img_obj.crop((x, (img_obj.height - h - y), x + w, y + h))
        return cropped_im

    def uri_for(self, name: str, atlas_name: str):
        try:
            matched = next(
                (atlas for atlas in self.atlases if atlas.name == atlas_name)
            )
        except StopIteration:
            raise KeyError(f"{atlas_name} not found")
        return f"atlas://{matched.path.with_suffix('')}/{name}"

    def category_image_listener(self, imgs: Sequence[tuple[str, Path]]):

        new_imgs = [
            (cname.lower(), img_path)
            for cname, img_path in imgs
            if f"category_img.{cname.lower()}" not in self
        ]
        if new_imgs:
            Logger.info(f"Found new Images {new_imgs}")
            img_sizes = asyncio.run(read_img_sizes([fp for _, fp in new_imgs]))
            # Size the atlas to fit the largest image
            k_large = max(
                ((a, b) for a, b in img_sizes.values()), key=lambda x: x[0] * x[1]
            )
            # Add padding
            k_large = max(k_large) + 4
            names, paths = [], []
            for cname, img_path in new_imgs:
                names.append(cname.lower())
                paths.append(img_path)
            self.save_to_atlas(
                images=paths,
                image_names=names,
                atlas_name="category_img",
                atlas_size=(k_large, k_large),
            )
