from typing import Union

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, OptionProperty, StringProperty

from domain.editable import EditableNote
from domain.events import CancelEditEvent, SaveNoteEvent
from utils import import_kv, sch_cb
from widgets.editor.editor import NoteEditor
from widgets.screens import InteractScreen

import_kv(__file__)


class NoteEditScreen(InteractScreen):
    """

    Displays Screen for Editing Existing Notes and Creating New Ones

    Attributes
    ----------
    mode: OptionProperty
        One of {'add', 'edit'}.
    init_text: StringProperty
        The initial text before any modifications
    note_editor: ObjectProperty

    """

    mode = OptionProperty("edit", options=["add", "edit"])
    init_text = StringProperty()
    note_editor: "NoteEditor" = ObjectProperty(rebind=True)

    def __init__(self, **kwargs):
        super(NoteEditScreen, self).__init__(**kwargs)
        app = App.get_running_app()
        app.bind(editor_note=self.handle_app_editor_note)
        app.bind(display_state=self.handle_app_display_state)

    def handle_app_display_state(self, instance, value):
        if value in {"add", "edit"}:
            Logger.debug(f"App Changed Mode : {value}")
            self.mode = value

    def on_note_editor(self, instance, value):
        self.note_editor.bind(on_save=self.handle_save)
        self.note_editor.bind(on_cancel=self.handle_cancel)
        self.bind(init_text=self.note_editor.setter("init_text"))
        self.bind(mode=self.note_editor.setter("mode"))

    def handle_app_editor_note(self, instance, value: Union["EditableNote", "None"]):
        """
        Tracks App.editor_note
        """
        if value is None:
            self.init_text = ""
            return

        self.init_text = value.edit_text

    def handle_cancel(self, *args, **kwargs):
        Logger.debug("Cancel Edit")

        app = App.get_running_app()
        app.registry.push_event(CancelEditEvent)
        clear_self_text = lambda x: setattr(self, "init_text", "")

        sch_cb(0, clear_self_text)

    def handle_save(self, *args, **kwargs):
        app = App.get_running_app()
        text = kwargs.get("text")
        title = kwargs.get("title")
        if text is None:
            raise ValueError("Expected text")

        app.registry.push_event(
            SaveNoteEvent(text=text, title=title, category=app.note_category)
        )

        clear_self_text = lambda x: setattr(self, "init_text", "")
        Clock.schedule_once(clear_self_text, 0)
