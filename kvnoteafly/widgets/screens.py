import os
from itertools import cycle
from typing import TYPE_CHECKING

from kivy import Logger
from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from toolz import sliding_window

from utils import import_kv

if TYPE_CHECKING:
    from widgets.categories import NoteCategoryButton
    from services.domain import MarkdownNoteDict

import_kv(__file__)


class NoteAppScreenManager(ScreenManager):
    app = ObjectProperty()
    play_state = StringProperty()

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.current = "chooser_screen"
        self.note_screen_cycler = self.make_note_cycler()
        self.last_note_screen = None
        self.app = app
        app.bind(display_state=self.handle_app_display_state)
        app.bind(play_state=self.handle_app_play_state)
        app.bind(needs_settings=self.handle_app_settings_state)

    def make_note_cycler(self):
        n_screens = 1 if os.environ.get("NO_TRANSITION", False) else 2
        for i in range(n_screens):
            note_screen = NoteCategoryScreen(name=f"note_screen{i}")
            self.add_widget(note_screen)
        return sliding_window(2, cycle(range(n_screens)))

    def category_selected(self, category: "NoteCategoryButton"):
        self.app.note_category = category.text

    def handle_app_settings_state(self, instance, needs_settings):
        if needs_settings:
            self.app.open_settings()

    def handle_app_display_state(self, instance, new):
        Logger.debug(f"ScreenManager: app_display_state : {new}")
        if new == "choose":  # Show the Category Selection Screen
            self.current = "chooser_screen"
        elif new == "display":
            self.handle_notes()
        elif new == "list":
            self.handle_notes_list_view()
        else:
            raise Exception(f"Unhandled display state {new}")

    def handle_app_play_state(self, instance, value):
        self.play_state = value
        for screen in self.screens:
            if screen.name.startswith("note_screen"):
                screen.current_note.note_title.button_bar.play_button.playing = (
                    value == "play"
                )

    def handle_notes(self, *args, **kwargs):
        last_active, next_active = next(self.note_screen_cycler)
        target = f"note_screen{next_active}"
        target_screen = next(screen for screen in self.screens if screen.name == target)
        self.last_note_screen = next_active
        self.current = target
        Clock.schedule_once(
            lambda dt: target_screen.set_note_content(self.app.note_data), 0
        )

    def handle_notes_list_view(self, *args, **kwargs):
        self.ids["list_view_screen"].set_note_list_view()
        self.current = "list_view_screen"


class NoteCategoryChooserScreen(Screen):
    chooser = ObjectProperty()
    categories = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def category_selected(self, category_btn: "NoteCategoryButton"):
        self.manager.category_selected(category_btn)


class NoteCategoryScreen(Screen):
    current_note = ObjectProperty()

    def set_note_content(self, note_data: "MarkdownNoteDict"):
        self.current_note.set_note_content(note_data)


class NoteListViewScreen(Screen):
    meta_notes = ListProperty()

    def set_note_list_view(self, *args, **kwargs):
        Clock.schedule_once(lambda dt: self.ids["scroller"].set(self.meta_notes), 0)
