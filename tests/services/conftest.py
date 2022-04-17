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
        category_file = (storage_directory / category).with_suffix(".md")
        with category_file.open(mode="w", encoding="utf-8") as note_doc:
            for note in notes:
                note_type = note["note_type"]
                note_text = note["text"]
                note_title = note["title"]
                note_doc.write(f"# {note_title}\n")
                if note_type == "code":
                    note_doc.write(f"```{category.lower()}\n")
                    note_doc.write(f"{note_text}\n")
                    note_doc.write("```")
                elif note_type == "shortcut":
                    note_doc.write(f"```shortcut\n")
                    note_doc.write(f"{note_text}\n")
                    note_doc.write("```")
                else:
                    note_doc.write(f"{note_text}\n")
                note_doc.write("\n")
    return storage_directory, data
