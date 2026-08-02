from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Protocol

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

    from mindref.lib.domain.protocols import AppRegistryProtocol


Builder.load_string("""
#:import DebugBoxLayout mindref.lib.widgets.behavior.DebugBoxLayout
#:import DebugFloatLayout mindref.lib.widgets.behavior.DebugFloatLayout
#:import HSeparator mindref.lib.widgets.separator.HSeparator
#:import LinearProgress mindref.lib.widgets.progress.LinearProgress

<NoteTitleInput@TextInput>
    size_hint_x: 1
    size_hint_y: None
    multiline: False
    height: self.minimum_height
    background_normal: ''
    background_active: ''
    background_color: 0, 0, 0, 0
    cursor_color: app.colors['Gray-600']
    foreground_color: 1, 1, 1, 1
    padding: [dp(8), (self.height - self.line_height) / 2, dp(8), 0]
    hint_text: "File Name"
    
    
    canvas.after:
        Color:
            rgba: [*app.colors['Gray-800'][:3], 0.1]
        RoundedRectangle:
            pos: [self.x, self.y - dp(8)]
            size: [self.width, self.height+(2*dp(8))]
            radius: [dp(4), dp(4), dp(4), dp(4)]
        Color:
            rgba: [*app.colors['Gray-800'][:3], 0.2] if not self.focus else [*app.colors['Gray-800'][:3], 0.4]
        Line:
            points: [self.x, self.y - dp(8), self.x + self.width, self.y - dp(8)]
            width: dp(1)

<DraftScreen>:
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
                NoteTitleInput:
                    id: title_input
                    text: ''                
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
                SaveDraftButton:
                    id: save_button
                    root: root
                    app: app
                    size_hint: (None, None)
                    pos_hint: {"center_y": 0.5}
                    text: "Save"
                    on_release: self.mutation(file_name=title_input.text, text=code_input.text)
                    disabled: not title_input.text
                    
""")


class LoadingStateProtocol(Protocol):
    """A widget whose loading state a child button drives."""

    is_loading: bool


class SaveDraftButton(LabelButton, LoadingButtonMixin):
    app: ObjectProperty[AppRegistryProtocol] = ObjectProperty()
    root: ObjectProperty[LoadingStateProtocol] = ObjectProperty()

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        self.mutation = Mutation(self.save_draft_on_app)
        self.mutation.bind(
            on_mutate=self.handle_on_mutate,
            on_resolved=self.handle_on_resolved,
        )

    def handle_on_mutate(self, *_args: object) -> None:
        self.disabled = True

    def handle_on_resolved(self, *_args: object) -> None:
        self.disabled = False
        self.root.is_loading = False

    def save_draft_on_app(self, file_name: str, text: str) -> None:
        self.root.is_loading = True
        self.app.save_draft_note(file_name, text)


class DraftScreenIds(NamedTuple):
    code_input: CodeInput
    layout: BoxLayout


class DraftScreen(Screen):
    ids: DraftScreenIds
    is_loading = BooleanProperty(False)
    app: ObjectProperty[AppRegistryProtocol] = ObjectProperty()
    lexer: ObjectProperty[Lexer] = ObjectProperty()

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        self.lexer = get_lexer_by_name("markdown")
