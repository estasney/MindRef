import tempfile
from pathlib import Path

import pytest
import yaml


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
