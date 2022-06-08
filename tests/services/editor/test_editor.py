import pytest

from services.editor.fileStorage import EditEvent, FileSystemEditor
from utils.registry import app_registry


@pytest.mark.parametrize("event", ("save", "cancel"))
def test_editor_registry(event: EditEvent, md_note):
    """
    Given Editor and edit_note
    Call registry listeners
    Check that edits, saves and cancels work
    Parameters
    ----------
    md_note

    Returns
    -------

    """
    editor = FileSystemEditor()
    edit_note = editor.edit_note(md_note)
    pre_text = edit_note.edit_text
    app_registry.note_editor.notify(event="edit", text="test123")
    assert edit_note.edit_text == "test123"
    assert edit_note.note.text == pre_text
    if event == "cancel":
        app_registry.note_editor.notify(event="cancel")
        assert edit_note.note.text == pre_text

    else:
        md_note_new = editor.save_note(edit_note)
        assert md_note_new.text == "test123"
