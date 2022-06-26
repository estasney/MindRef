import pytest
from adapters.notes.fs.fs_note_repository import FileSystemNoteRepository


@pytest.mark.parametrize("n_categories", [0, 1, 2, 3])
def test_category_discovery(n_categories, category_folders):
    expected_folders, root_folder = category_folders(n_categories)
    fs = FileSystemNoteRepository(new_first=True)
    fs.storage_path = root_folder
    for folder, _ in expected_folders:
        assert folder.name in fs.categories
