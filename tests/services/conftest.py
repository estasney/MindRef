import tempfile
from pathlib import Path

import pytest
import yaml
from PIL import Image, ImageDraw


@pytest.fixture(scope="session")
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


@pytest.fixture()
def stored_atlas(storage_directory):
    def _stored_atlas(atlas_name, *img_names):
        atlas_folder_path = storage_directory / atlas_name
        atlas_folder_path.mkdir()
        img_files = []
        for im in img_names:
            img_path = atlas_folder_path / im
            img_path = img_path.with_suffix(".png")
            img = Image.new(mode="RGB", size=(24, 24))
            draw = ImageDraw.Draw(img)
            draw.line((0, 0, *img.size), fill=128, width=10)
            img.save(img_path)
            img_files.append(str(img_path))
        import os

        os.environ["KIVY_NO_ARGS"] = "1"
        from kivy.atlas import Atlas

        Atlas.create(str(atlas_folder_path / atlas_name), img_files, (24 * 4, 24 * 4))
        for im in img_names:
            img_path = atlas_folder_path / im
            img_path.with_suffix(".png").unlink()
        return atlas_folder_path

    return _stored_atlas
