from typing import TYPE_CHECKING, Union

from kivy import Logger
from kivy.properties import ObjectProperty, OptionProperty, StringProperty

from lib.domain.editable import EditableNote
from lib.domain.events import CancelEditEvent, SaveNoteEvent
from lib.utils import attrsetter, import_kv, sch_cb, get_app
from lib.widgets.editor.note_editor import NoteEditor
from lib.widgets.screens import InteractScreen

if TYPE_CHECKING:
    from lib import DISPLAY_STATE

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
        app = get_app()
        app.bind(editor_note=self.handle_app_editor_note)
        app.bind(display_state=self.handle_app_display_state)

    def handle_app_display_state(self, _, value: "DISPLAY_STATE"):
        _, new = value
        if new in {"add", "edit"}:
            Logger.debug(f"App Changed Mode : {value}")
            self.mode = new

    def on_note_editor(self, *_args):
        self.note_editor.bind(on_save=self.handle_save)
        self.note_editor.bind(on_cancel=self.handle_cancel)
        self.bind(init_text=self.note_editor.setter("init_text"))
        self.bind(mode=self.note_editor.setter("mode"))

    def handle_app_editor_note(self, _, value: Union["EditableNote", "None"]):
        """
        Tracks App.editor_note
        """
        if value is None:
            self.init_text = ""
            return

        self.init_text = value.edit_text

    def handle_cancel(self, *_args):
        Logger.debug(f"{type(self).__name__}: Cancel Edit")
        app = get_app()
        app.registry.push_event(CancelEditEvent())

    def handle_save(self, *_args, **kwargs):
        app = get_app()
        text = kwargs.get("text")
        title = kwargs.get("title")
        Logger.info(f"{type(self).__name__}: Save Note - {title} = {app.note_category}")
        if text is None:
            raise ValueError("Expected text")

        app.registry.push_event(
            SaveNoteEvent(text=text, title=title, category=app.note_category)
        )

        clear_init_text = attrsetter(self, "init_text", "")
        sch_cb(clear_init_text, timeout=0.1)
