from typing import TYPE_CHECKING, NamedTuple, Optional

from mindref.lib import import_kv

import_kv(__file__)

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from pygments.lexers import get_lexer_by_name

if TYPE_CHECKING:
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.codeinput import CodeInput
    from pygments.lexer import Lexer

    from mindref.app_notes import NoteFile
    from mindref.lib.domain.protocols import AppRegistryProtocol


class EditScreenIds(NamedTuple):
    code_input: "CodeInput"
    layout: "BoxLayout"


class EditScreen(Screen):
    ids: EditScreenIds

    app: "AppRegistryProtocol" = ObjectProperty()
    lexer: "Lexer" = ObjectProperty()
    editing_note: "NoteFile" = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lexer = get_lexer_by_name("markdown")
        Clock.schedule_once(self._bind_editing_note, 0)

    def _bind_editing_note(self, _dt):
        self.app.bind(editing_note=self.setter("editing_note"))

    def on_editing_note(self, _instance, value: Optional["NoteFile"]):
        editor = self.ids.code_input
        if not value:
            editor.text = ""
            return True
        text = value.read_text()
        editor.text = text
        return True
