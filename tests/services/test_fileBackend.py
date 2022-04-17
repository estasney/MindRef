from services.backend.fileBackend import FileSystemBackend
from services.domain import CodeNote, MarkdownNote, ShortcutNote


def test_categories(stored_categories):
    storage_folder, data = stored_categories
    categories = list(data.keys())
    fs = FileSystemBackend(storage_folder)
    assert set(fs.categories) == set(categories)


def test_parse_category_notes(stored_categories):
    storage_folder, data = stored_categories
    fs = FileSystemBackend(storage_folder)
    parsed_notes = fs.parse_category_notes()
    assert isinstance(parsed_notes, list)
    for category, notes in data.items():
        for i, note in enumerate(notes):
            note_type = note["note_type"]
            note_text = note["text"]
            note_title = note["title"]
            if note_type == "code":
                data_note = CodeNote(
                    idx=i,
                    title=note_title,
                    category=category,
                    text=note_text,
                    lexer=category.lower(),
                )
            elif note_type == "shortcut":
                data_note = ShortcutNote(
                    idx=i, title=note_title, category=category, keys_str=note_text
                )
            elif note_type == "text":
                data_note = MarkdownNote(
                    idx=i, title=note_title, category=category, text=note_text
                )
            else:
                raise
            assert data_note in parsed_notes
