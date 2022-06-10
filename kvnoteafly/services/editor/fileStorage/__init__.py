import weakref

from kivy.logger import Logger

from services.domain import MarkdownNote
from services.editor import EditableNote, EditorProtocol, NoteServiceApp
from typing import Literal

EditEvent = Literal["edit", "save", "cancel"]


class FileSystemEditor(EditorProtocol):
    def __init__(self):
        self.edit_listener = None

    def new_note(self) -> EditableNote:
        pass

    def edit_note(self, note: MarkdownNote) -> EditableNote:
        """
        Get an editable note

        Listens for note_editor topic
        - edit
        - save
        - cancel
        """
        from utils.registry import app_registry

        Logger.debug("Editor: Editing Note")
        edit_note = EditableNote(note=note)

        def teardown_listener():
            Logger.debug("Teardown EditableNote Listener")
            app_registry.note_editor.remove_listener(listener)

        def listener(event: EditEvent, **kwargs):
            Logger.debug(f"EditableNote Listener Got Event {event} {kwargs}")
            if event == "cancel":
                return teardown_listener()
            elif event == "save":
                teardown_listener()
            func = getattr(self, f"_{event}_listener")
            func(edit_note, **kwargs)

        app_registry.note_editor.add_listener(listener)
        self.edit_listener = weakref.ref(listener)
        return edit_note

    def _edit_listener(self, note: EditableNote, **kwargs):
        Logger.debug("Got Edit")
        note.edit_text = kwargs.get("text")

    def _save_listener(self, note: EditableNote, **kwargs):
        Logger.debug("Got Save")
        md_note = self.save_note(note)
        cb = kwargs.get("cb")
        if cb:
            cb(md_note)

    def save_note(self, note: EditableNote) -> MarkdownNote:
        md_note = note.note
        md_note.file.write_text(note.edit_text, encoding="utf-8")
        Logger.debug(f"Saved File To {md_note.file}")
        if self.edit_listener is not None:
            from utils.registry import app_registry

            try:
                app_registry.note_editor.remove_listener(self.edit_listener())
            except ValueError:
                ...
            self.edit_listener = None
        return MarkdownNote(
            category=md_note.category, idx=md_note.idx, file=md_note.file
        )

    def edit_current_note(self, app: NoteServiceApp) -> EditableNote:
        current = app.note_service.current_note()
        return self.edit_note(current)
