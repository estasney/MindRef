from __future__ import annotations

import weakref

from kivy.logger import Logger

from services.domain import MarkdownNote
from services.editor import EditableNote, EditorProtocol, NoteServiceApp, TextNote
from typing import Callable, Literal, Optional, overload

EditEvent = Literal["edit", "save", "cancel"]
NoteAction = Literal["edit", "add"]


class FileSystemEditor(EditorProtocol):
    def __init__(self):
        self.edit_listener = None

    def new_note(self) -> TextNote:
        """
        Get an editable note from empty source

        Listens for note_editor topic
        - add
        - save
        - cancel

        Returns
        -------

        """
        return self._generic_note_action(None, "add")

    def edit_note(self, note: MarkdownNote) -> EditableNote:
        """
        Get an editable note

        Listens for note_editor topic
        - edit
        - save
        - cancel
        """
        return self._generic_note_action(note, "edit")

    @overload
    def _generic_note_action(
        self, note: MarkdownNote, action: Literal["edit"]
    ) -> EditableNote:
        ...

    @overload
    def _generic_note_action(self, note: None, action: Literal["add"]) -> TextNote:
        ...

    def _generic_note_action(self, note, action: NoteAction):
        """
        Edit or New Note

        Parameters
        ----------
        note : Required for edit

        Returns
        -------

        """
        from utils.registry import app_registry

        Logger.debug(f"Editor: {'Editing' if action == 'edit' else 'Create New'} Note")

        if action == "edit":
            data_note = EditableNote(note=note)
        elif action == "add":
            data_note = TextNote()
        else:
            raise ValueError(f"Unhandled action {action}")

        def teardown_listener():
            app_registry.note_editor.remove_listener(listener)

        def listener(event: EditEvent, **kwargs):
            Logger.debug(f"Listener Got Event {event} {kwargs}")
            if event == "cancel":
                return teardown_listener()
            elif event == "save":
                teardown_listener()
            func = getattr(self, f"_{event}_listener")
            func(data_note, **kwargs)

        app_registry.note_editor.add_listener(listener)
        self.edit_listener = weakref.ref(listener)
        return data_note

    def _edit_listener(self, note: EditableNote | TextNote, **kwargs):
        Logger.debug(f"Got Edit for Note Type: {note.__class__.__name__}")
        if hasattr(note, "edit_text"):
            note.edit_text = kwargs.get("text")
        else:
            note.text = kwargs.get("text")

    def _save_listener(self, note: EditableNote | TextNote, **kwargs):
        Logger.debug(f"Got Save For Note Type: {note.__class__.__name__}")
        cb = kwargs.pop("callback")
        if not cb:
            raise AttributeError("No callback included")
        self.save_note(note, callback=cb, **kwargs)

    def save_note(
        self,
        note: EditableNote | TextNote,
        callback: Callable[[MarkdownNote], None],
        **kwargs,
    ):
        """
        Save either an edited note or create a new one
        Parameters
        ----------
        note : EditableNote or TextNote
        callback: Callable
            Takes
        kwargs:
            When passing TextNote, include 'category' and 'filename'

        Returns
        -------
        """
        from utils.registry import app_registry

        if isinstance(note, TextNote):

            note_category = kwargs.get("category")
            note_filename = kwargs.get("filename")
            if not all((note_category, note_filename)):
                raise AttributeError(f"Pass category and filename when saving TextNote")
            note.category = note_category
            note.filename = note_filename
            app_registry.note_files.notify("save_note", note, callback)

        elif isinstance(note, EditableNote):
            app_registry.note_files.notify("save_note", note, callback)
        else:
            raise ValueError(f"Not of type: {note}, {type(note)}")

        if self.edit_listener is not None:
            from utils.registry import app_registry

            try:
                app_registry.note_editor.remove_listener(self.edit_listener())
            except ValueError:
                ...
            self.edit_listener = None

    def edit_current_note(self, app: NoteServiceApp) -> EditableNote:
        current = app.note_service.current_note()
        return self.edit_note(current)
