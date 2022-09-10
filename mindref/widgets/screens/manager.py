from typing import Callable

from kivy import Logger
from kivy.clock import Clock
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from utils import import_kv, sch_cb
from utils.index import RollingIndex
from utils.triggers import trigger_factory
from widgets.app_menu.app_menu import AppMenu
from widgets.behavior.interact_behavior import InteractBehavior
from widgets.buttons.category import NoteCategoryButton

import_kv(__file__)


class NoteAppScreenManager(InteractBehavior, ScreenManager):
    app = ObjectProperty()
    play_state = StringProperty()
    menu_open = BooleanProperty(False)
    reversed_transition = BooleanProperty(False)
    screen_triggers: Callable[[str], None]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_screen_cycler = RollingIndex(size=2)
        self.current = "chooser_screen"
        self.menu = None
        self.note_trigger = Clock.create_trigger(self.handle_notes)
        self.app.bind(display_state=self.handle_app_display_state)
        self.app.bind(note_data=self.note_trigger)
        self.app.bind(play_state=self.setter("play_state"))
        self.app.bind(screen_transitions=self.setter("screen_transitions"))
        self.app.bind(menu_open=self.setter("menu_open"))
        self.fbind("menu_open", self.handle_menu_state)
        self.fbind("reversed_transition", self.handle_reversed_transition)
        self.screen_triggers = trigger_factory(self, "current", self.screen_names)

    def handle_menu_state(self, instance, menu_open: bool):
        def resume_temp_pause(*args):
            Logger.debug("Resume Temp Pause")
            self.app.play_state = "play"

        def remove_from_screen(*args):
            Logger.debug("Remove Menu")
            self.current_screen.remove_widget(self.menu)
            self.menu = None

        Logger.debug(f"Menu Open {menu_open}")
        if menu_open:
            view = AppMenu()
            self.menu = view
            temp_pause = self.play_state == "play"
            self.current_screen.add_widget(view)
            if temp_pause:
                view.fbind("on_dismiss", resume_temp_pause)
            view.fbind("on_dismiss", remove_from_screen)
        else:
            self.menu.dispatch("on_dismiss")

    def category_selected(self, category: "NoteCategoryButton"):
        self.app.registry.set_note_category(category.text, on_complete=None)

    def handle_reversed_transition(self, instance, value):
        if self.reversed_transition:
            self.transition = SlideTransition(direction="right")
        else:
            self.transition = SlideTransition(direction="left")

    def handle_app_display_state(self, instance, new):
        Logger.debug(f"ScreenManager: app_display_state : {new}")
        if new == "choose":  # Show the Category Selection Screen
            self.screen_triggers("chooser_screen")
        elif new == "display":
            self.note_trigger()
        elif new == "list":
            self.handle_notes_list_view()
        elif new == "edit":
            self.handle_notes_edit_view()
        elif new == "add":
            self.handle_notes_add_view()
        elif new == "error":
            self.handle_error_message()

        else:
            raise Exception(f"Unhandled display state {new}")

    def handle_app_play_state(self, instance, value):
        self.play_state = value

    def handle_notes(self, *args, **kwargs):

        (
            current_screen_idx,
            next_screen_idx,
        ) = self.note_screen_cycler.current, self.note_screen_cycler.next(peek=True)
        target_name = f"note_screen_{next_screen_idx}"
        current_name = f"note_screen_{current_screen_idx}"
        target_screen = next(
            screen for screen in self.screens if screen.name == target_name
        )
        current_screen = next(
            screen for screen in self.screens if screen.name == current_name
        )

        # Call trigger to update current screen

        update_current_screen = lambda x: self.screen_triggers(target_screen.name)

        # Set note data
        data = {k: v for k, v in self.app.note_data.items()}
        set_data = lambda dt: target_screen.set_note_content(data)

        # Clear note data from last screen
        clear_data = lambda dt: current_screen.set_note_content(None)

        # Advance index
        advance_index = lambda dt: self.note_screen_cycler.next()

        sch_cb(0, set_data, update_current_screen, clear_data, advance_index)

    def handle_notes_list_view(self, *args, **kwargs):
        self.screen_triggers("list_view_screen")

    def handle_notes_edit_view(self, *args, **kwargs):
        Logger.debug(f"{self.__class__.__name__} : Switching to note_edit_screen")
        self.screen_triggers("note_edit_screen")

    def handle_notes_add_view(self, *args, **kwargs):
        Logger.debug(
            f"{self.__class__.__name__} : Switching to note_edit_screen - Adding Note"
        )
        self.screen_triggers("note_edit_screen")

    def handle_error_message(self, *args, **kwargs):
        Logger.debug(f"{self.__class__.__name__} : Switching to error_message_screen")
        self.screen_triggers("error_message_screen")
