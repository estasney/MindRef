from mindref.lib.domain.editable import EditableNote


def test_editable_note_post_init(md_note):
    edit_note = EditableNote.from_markdown_note(md_note)
    assert edit_note.edit_text == md_note.text
