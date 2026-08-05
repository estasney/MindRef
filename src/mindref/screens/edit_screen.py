from typing import TYPE_CHECKING, NamedTuple

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from pygments.lexers import get_lexer_by_name

from mindref.lib.mutation import Mutation
from mindref.lib.widgets.buttons.buttons import LabelButton, LoadingButtonMixin

if TYPE_CHECKING:
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.codeinput import CodeInput
    from pygments.lexer import Lexer

    from mindref.app_notes import NoteFile
    from mindref.lib.domain.protocols import AppRegistryProtocol

Builder.load_string("""
#:import DebugBoxLayout mindref.lib.widgets.behavior.DebugBoxLayout
#:import DebugFloatLayout mindref.lib.widgets.behavior.DebugFloatLayout
#:import HSeparator mindref.lib.widgets.separator.HSeparator
#:import LinearProgress mindref.lib.widgets.progress.LinearProgress

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
                    font_size: sp(app.base_font_size + 4)
                    halign: 'center'
                    valign: 'center'
        HSeparator:
            color: [*app.colors['Gray-800'][:3], .2]
            height: dp(1)        
        CodeInput:
            id: code_input
            input_type: 'text'
            pos_hint: {"top": 1}
            size_hint_x: 1
            size_hint_y: .9
            lexer: root.lexer
            style_name: 'github-dark'
            font_family: app.fonts['mono']
            font_size: sp(app.base_font_size)
        LinearProgress:
            id: progress_bar
            size_hint_y: None
            height: dp(4)
            animated: root.is_loading
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
                    id: cancel_button
                    root: root 
                    app: app
                    size_hint: (None, None)
                    pos_hint: {"center_y": 0.5}
                    color: app.colors['Warn']
                    text: "Cancel"
                    on_release: self.mutation()
                SaveEditButton:
                    id: save_button
                    root: root
                    app: app
                    size_hint: (None, None)
                    pos_hint: {"center_y": 0.5}
                    text: "Save"
                    on_release: self.mutation(code_input.text)
""")


class CancelEditButton(LabelButton, LoadingButtonMixin):
    app: "ObjectProperty[AppRegistryProtocol]" = ObjectProperty()
    root: "ObjectProperty[EditScreen]" = ObjectProperty()

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        self.mutation = Mutation(self.cancel_edit_on_app)
        self.mutation.bind(
            on_mutate=self.handle_on_mutate,
            on_resolved=self.handle_on_resolved,
        )

    def handle_on_mutate(self, _instance: object) -> None:
        self.disabled = True

    def handle_on_resolved(self, _instance: object) -> None:
        self.disabled = False
        self.root.is_loading = False

    def cancel_edit_on_app(self) -> None:
        self.root.is_loading = True
        self.app.cancel_edit_note()


class SaveEditButton(LabelButton, LoadingButtonMixin):
    app: "ObjectProperty[AppRegistryProtocol]" = ObjectProperty()
    root: "ObjectProperty[EditScreen]" = ObjectProperty()

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        self.mutation = Mutation(self.save_edit_on_app)
        self.mutation.bind(
            on_mutate=self.handle_on_mutate,
            on_resolved=self.handle_on_resolved,
        )

    def handle_on_mutate(self, _instance: object) -> None:
        self.disabled = True

    def handle_on_resolved(self, _instance: object) -> None:
        self.disabled = False
        self.root.is_loading = False

    def save_edit_on_app(self, text: str) -> None:
        self.root.is_loading = True
        self.app.save_edit_note(text)


class EditScreenIds(NamedTuple):
    code_input: "CodeInput"
    layout: "BoxLayout"


class EditScreen(Screen):
    ids: EditScreenIds
    is_loading = BooleanProperty(False)
    app: "ObjectProperty[AppRegistryProtocol]" = ObjectProperty()
    lexer: "ObjectProperty[Lexer]" = ObjectProperty()
    editing_note: "ObjectProperty[NoteFile | None]" = ObjectProperty(allownone=True)

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        self.lexer = get_lexer_by_name("markdown")
        Clock.schedule_once(self._bind_editing_note, 0)

    def _bind_editing_note(self, _dt: float) -> None:
        self.app.bind(editing_note=self.setter("editing_note"))

    def on_editing_note(self, _instance: object, value: "NoteFile | None") -> bool:
        editor = self.ids.code_input
        if not value:
            editor.text = ""
            return True
        text = value.read_text()
        editor.text = text
        return True
