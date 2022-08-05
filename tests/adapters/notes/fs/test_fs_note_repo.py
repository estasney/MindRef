import pytest
from adapters.notes.fs.fs_note_repository import FileSystemNoteRepository


@pytest.mark.parametrize("n_categories", [0, 1, 2, 3])
def test_category_discovery(n_categories, category_folders):
    expected_folders, root_folder = category_folders(n_categories)
    fs = FileSystemNoteRepository(new_first=True, get_app=lambda: None)
    fs.storage_path = root_folder
    discovery = list(fs.discover_notes())
    for folder, img in expected_folders:
        assert folder.name in fs.categories
        assert folder.name in ((d.category for d in discovery))
        assert img in ((d.image_path for d in discovery))
