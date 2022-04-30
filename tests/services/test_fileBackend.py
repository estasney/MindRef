from services.backend.fileStorage import FileSystemBackend
from services.domain import MarkdownNote


def test_categories(stored_categories):
    storage_folder, data = stored_categories
    categories = list(data.keys())
    fs = FileSystemBackend(storage_folder)
    assert set(fs.categories) == set(categories)
