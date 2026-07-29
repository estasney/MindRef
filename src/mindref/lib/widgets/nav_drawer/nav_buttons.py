from __future__ import annotations

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from mindref.lib.utils import get_app
from mindref.lib.widgets.buttons.buttons import ThemedIconButton


class OpenMenuButton(ThemedIconButton): ...


Builder.load_string(
    """
<OpenMenuButton>:
    icon_code: '\ue5d2'
    background_color: (0, 0, 0, 0)
    color: (1.0, 1.0, 1.0, 1.0) if self.state == 'down' else (1.0, 1.0, 1.0, 0.5)


<ClearSearchButton@ThemedIconButton>:
    icon_code: "\ue5cd"
    size_hint: (None, None)

    background_color: (0, 0, 0, 0)
    color: (1.0, 1.0, 1.0, 0.5)
    pos_hint: {"center_y": 0.5}

<SettingsButton@ThemedIconButton>:
    icon_code: "\ue8b8"
    size_hint: (None, None)
    background_color: (0,0,0,0)
    color: (1.0, 1.0, 1.0, 0.5)
    pos_hint: {"center_y": 0.5}

<NewNoteButton@ThemedIconButton>:
    icon_code: "\ue89c"
    size_hint: (None, None)
    background_color: (0, 0, 0, 0)
    color: (1.0, 1.0, 1.0)
    pos_hint: {"center_y": 0.5}
    opacity: 0


<EditNoteButton@ThemedIconButton>:
    icon_code: "\uf88c"
    size_hint: (None, None)
    background_color: (0, 0, 0, 0)
    color: (1.0, 1.0, 1.0)
    pos_hint: {"center_y": 0.5}
    opacity: 0

<NoteActionsContainer@BoxLayout>:
    orientation: "horizontal"
    pos_hint: {"center_y": 0.5, "right": 1.0}
    width: self.minimum_width
    size_hint_x: None
    opacity: 0
"""
)


class ClearSearchButton(ThemedIconButton): ...


class SettingsButton(ThemedIconButton): ...


class NewNoteButton(ThemedIconButton): ...


class EditNoteButton(ThemedIconButton): ...


class NoteActionsContainer(BoxLayout):
    new_note_button: ObjectProperty[NewNoteButton | None] = ObjectProperty(
        allownone=True
    )
    edit_note_button: ObjectProperty[EditNoteButton | None] = ObjectProperty(
        allownone=True
    )
    nav_id_selected = StringProperty(None, allownone=True)
    button_opacity = NumericProperty(0)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        Clock.schedule_once(self.attach, 0)

    def on_nav_id_selected(self, _instance: object, value: str) -> bool:
        if value:
            Clock.schedule_once(self.attach_edit_note_button, 0)
        else:
            Clock.schedule_once(self.detach_edit_note_button, 0)
        return True

    def handle_edit_note(self, *_args: object) -> bool:
        if not self.nav_id_selected:
            Logger.warning("EditNoteButton: No note selected to edit.")
            return True
        get_app().edit_note(self.nav_id_selected)
        return True

    def handle_draft_note(self, *_args: object) -> bool:
        get_app().draft_note()
        return True

    def attach_new_note_button(self, _dt: float) -> None:
        if self.new_note_button is None:
            self.new_note_button = NewNoteButton()
            self.new_note_button.bind(
                height=self.new_note_button.setter("width"),
                on_release=self.handle_draft_note,
            )
            self.bind(button_opacity=self.new_note_button.setter("opacity"))
            self.add_widget(self.new_note_button)

    def detach_new_note_button(self, _dt: float) -> None:
        if self.new_note_button is not None:
            self.remove_widget(self.new_note_button)
            self.new_note_button = None

    def attach_edit_note_button(self, _dt: float) -> None:
        if self.edit_note_button is None:
            self.edit_note_button = EditNoteButton()
            self.edit_note_button.bind(
                height=self.edit_note_button.setter("width"),
                on_release=self.handle_edit_note,
            )
            self.bind(button_opacity=self.edit_note_button.setter("opacity"))
            self.add_widget(self.edit_note_button, index=0)

    def detach_edit_note_button(self, _dt: float) -> None:
        if self.edit_note_button is not None:
            self.remove_widget(self.edit_note_button)
            self.edit_note_button = None

    def attach(self, _dt: float) -> None:
        Clock.schedule_once(self.attach_new_note_button, 0)
        if self.nav_id_selected:
            Clock.schedule_once(self.attach_edit_note_button, 0)

    def detach(self) -> None:
        Clock.schedule_once(self.detach_new_note_button, 0)
        Clock.schedule_once(self.detach_edit_note_button, 0)

    def on_opacity(self, instance: object, value: float) -> None:
        """Update the opacity of the buttons based on the button_opacity property"""
        self.button_opacity = value / 2
