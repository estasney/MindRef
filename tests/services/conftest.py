import string
import tempfile
from pathlib import Path
from typing import Literal, Sequence
from string import ascii_letters, digits
import pytest
import yaml
import random
from PIL import Image, ImageDraw


@pytest.fixture()
def storage_directory():
    temp_dir = tempfile.TemporaryDirectory()
    yield Path(temp_dir.name)
    temp_dir.cleanup()


@pytest.fixture()
def stored_categories(storage_directory):
    data_path = Path(__file__).parent / "data" / "notes.yaml"
    with data_path.open(mode="r", encoding="utf-8") as fp:
        data = yaml.load(fp, Loader=yaml.FullLoader)
    for category, notes in data.items():
        category_folder = storage_directory / category
        category_folder.mkdir()
        for note in notes:
            note_file = (category_folder / category).with_suffix(".md")
            with note_file.open(mode="w", encoding="utf-8") as note_doc:
                note_doc.write(f"# {note['text']}\n{note['title']}\n")

    return storage_directory, data


def img_maker(width, height):

    img = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(img)
    draw.line((0, 0, *img.size), fill=128, width=10)
    return img


def static_vars(**kwargs):
    def wrapped_func(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return wrapped_func


@pytest.fixture()
def img_name():
    @static_vars(seen=set([]))
    def _img_name(pool: Sequence[str], name_len: tuple[int, int]):
        while True:
            img_name_len = random.randint(*name_len)
            img_letters = random.choices(pool, k=img_name_len)
            img_n = "".join(img_letters)
            if img_n not in _img_name.seen:
                _img_name.seen.add(img_n)
                return img_n

    return _img_name


@pytest.fixture()
def stored_atlas(storage_directory, img_name):
    def _stored_atlas(atlas_name, atlas_type: Literal["mono", "multi"], n_images):
        WIDTH, HEIGHT = 10, 10
        NAME_POOL = string.ascii_letters + string.digits
        atlas_folder_path = storage_directory / atlas_name
        atlas_folder_path.mkdir()
        img_files = []
        img_names = []
        for i in range(n_images):
            im = img_name(NAME_POOL, (1, 16))
            img_path = atlas_folder_path / im
            img_path = img_path.with_suffix(".png")
            img = img_maker(WIDTH, HEIGHT)
            img.save(img_path)
            img_files.append(str(img_path))
            img_names.append(img_path.stem)
        import os

        os.environ["KIVY_NO_ARGS"] = "1"
        from kivy.atlas import Atlas

        # mono atlas can hold all images
        # multi is split across several
        if atlas_type == "mono":
            atlas_size = (WIDTH * (n_images + 1), HEIGHT * (n_images + 1))
        else:
            atlas_size = (WIDTH + 2, HEIGHT + 2)
        Atlas.create(str(atlas_folder_path / atlas_name), img_files, size=atlas_size)
        for im in img_names:
            img_path = atlas_folder_path / im
            img_path.with_suffix(".png").unlink()
        return atlas_folder_path, img_names

    return _stored_atlas
