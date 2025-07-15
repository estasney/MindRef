from typing import TYPE_CHECKING, NamedTuple, Optional

from kivy import Logger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from pygments.lexers import get_lexer_by_name

from mindref.lib import get_app
from mindref.lib.mutation import Mutation
from mindref.lib.widgets.buttons.buttons import LabelButton

if TYPE_CHECKING:
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.codeinput import CodeInput
    from pygments.lexer import Lexer

    from mindref.app_notes import NoteFile
    from mindref.lib.domain.protocols import AppRegistryProtocol

Builder.load_string("""
#:import DebugBoxLayout mindref.lib.widgets.behavior.DebugBoxLayout
#:import DebugFloatLayout mindref.lib.widgets.behavior.DebugFloatLayout
#:import ThemedLabelButton mindref.lib.widgets.buttons.buttons.ThemedLabelButton
#:import ContainedLabelButton mindref.lib.widgets.buttons.buttons.ContainedLabelButton
#:import LabelButton mindref.lib.widgets.buttons.buttons.LabelButton
#:import HSeparator mindref.lib.widgets.separator.HSeparator


 
<EditScreen>:
    app: app
    canvas.before:
        Color:
            rgba: app.colors['Dark']
        Rectangle:
            size: self.size
            pos: self.pos
    DebugBoxLayout:
        id: layout
        debug_layout: False
        orientation: 'vertical'
        DebugFloatLayout:
            id: title_bar
            debug_layout: False
            size_hint_x: 1
            size_hint_y: .07
            pos_hint: {"top": 1}
            canvas:
                Color:
                    rgba: app.colors['RichBlack']
                Rectangle:
                    size: self.size
                    pos: self.pos
            DebugBoxLayout:
                height: self.minimum_height
                size_hint_y: None
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                Label:
                    id: title_label
                    text: root.editing_note.label if root.editing_note else ""
                    text_size: root.width, None
                    size: self.texture_size
                    font_size: app.base_font_size + dp(4)
                    halign: 'center'
                    valign: 'center'
        HSeparator:
            color: [*app.colors['Gray-800'][:3], .2]
            height: dp(1)        
        CodeInput:
            id: code_input
            pos_hint: {"top": 1}
            size_hint_x: 1
            size_hint_y: .9
            lexer: root.lexer
            style_name: 'github-dark'
            font_family: app.fonts['mono']
            font_size: app.base_font_size
        DebugFloatLayout:
            debug_layout: False
            id: bottom_bar
            size_hint_x: 1
            size_hint_y: .1
            pos_hint: {"bottom": 1}
            canvas:
                Color:
                    rgba: app.colors['RichBlack']
                Rectangle:
                    size: self.size
                    pos: self.pos
            DebugBoxLayout:
                id: button_bar
                debug_layout: False
                orientation: 'horizontal'
                size_hint_y: 1
                size_hint_x: None
                width: self.minimum_width
                pos_hint: {"right": 1, "y": 0}
                padding: [dp(8), dp(8), dp(8), dp(8)]
                spacing: dp(8)
                CancelEditButton:
                    size_hint: (None, None)
                    pos_hint: {"center_y": 0.5}
                    color: app.colors['Warn']
                    text: "Cancel"
                    on_release: self.mutation()
                SaveEditButton:
                    size_hint: (None, None)
                    pos_hint: {"center_y": 0.5}
                    text: "Save"
                    on_release: self.mutation(code_input.text)
            
            
            """)


class CancelEditButton(LabelButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mutation = Mutation(self.cancel_edit_on_app)
        self.mutation.bind(
            on_mutate=self.handle_on_mutate,
            on_resolved=self.handle_on_resolved,
        )

    def handle_on_mutate(self, _dt):
        self.disabled = True

    def handle_on_resolved(self, _dt):
        self.disabled = False

    def cancel_edit_on_app(self):
        app = get_app()
        app.cancel_edit_note()


class SaveEditButton(LabelButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mutation = Mutation(self.save_edit_on_app)
        self.mutation.bind(
            on_mutate=self.handle_on_mutate,
            on_resolved=self.handle_on_resolved,
        )

    def handle_on_mutate(self, _dt):
        self.disabled = True

    def handle_on_resolved(self, _dt):
        self.disabled = False

    def save_edit_on_app(self, text: str):
        app = get_app()
        app.save_edit_note(text)


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
