from contextlib import nullcontext as should_succeed
from services.editor import EditableNote
from services.editor.fileStorage import FileSystemEditor


def test_editable_note_save(md_note):
    edit_note = EditableNote(note=md_note)
    editor = FileSystemEditor()
    with should_succeed():
        edit_note.save(editor)


def test_editable_note_post_init(md_note):
    edit_note = EditableNote(md_note)
    assert edit_note.edit_text == md_note.text
