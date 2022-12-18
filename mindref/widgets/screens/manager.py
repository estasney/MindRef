from typing import Callable, TYPE_CHECKING

from kivy import Logger
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from utils import caller, import_kv, sch_cb
from utils.index import RollingIndex
from utils.triggers import trigger_factory
from widgets.app_menu.app_menu import AppMenu
from widgets.behavior.interact_behavior import InteractBehavior
from widgets.behavior.refresh_behavior import RefreshBehavior
from widgets.buttons.category import NoteCategoryButton

if TYPE_CHECKING:
    from mindref.mindref import DISPLAY_STATE
    from domain.events import PAGINATION_DIRECTION
    from domain.markdown_note import MarkdownNoteDict

import_kv(__file__)


class NoteAppScreenManager(InteractBehavior, RefreshBehavior, ScreenManager):
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
        self.app.bind(display_state=self.handle_app_display_state)
        self.app.bind(on_paginate=self.handle_pagination)
        self.app.bind(play_state=self.setter("play_state"))
        self.app.bind(menu_open=self.setter("menu_open"))
        self.fbind("menu_open", self.handle_menu_state)
        self.fbind("reversed_transition", self.handle_reversed_transition)
        self.screen_triggers = trigger_factory(self, "current", self.screen_names)

    def on_refresh(self, state: bool):
        self.dispatch_children("on_refresh", state)
        return True

    def handle_menu_state(self, _, menu_open: bool):
        def resume_temp_pause(*_args):
            Logger.debug("Resume Temp Pause")
            self.app.play_state = "play"

        def remove_from_screen(*_args):
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

        elif not menu_open and self.menu:
            self.menu.dispatch("on_dismiss")

    def category_selected(self, category: "NoteCategoryButton"):
        self.app.registry.set_note_category(category.text, on_complete=None)

    def handle_reversed_transition(self, *_args):
        if self.reversed_transition:
            self.transition = SlideTransition(direction="right")
        else:
            self.transition = SlideTransition(direction="left")

    def handle_app_display_state(self, _, value: "DISPLAY_STATE"):
        old, new = value
        Logger.debug(f"ScreenManager: app_display_state - {old} -> {new}")
        match (old, new):
            case (_, "choose"):
                self.screen_triggers("chooser_screen")
            case ("display", "display"):
                ...
            case (_, "display"):
                self.handle_notes_display_view()
            case (_, "list"):
                self.handle_notes_list_view()
            case (_, "edit"):
                self.handle_notes_edit_view()
            case (_, "add"):
                self.handle_notes_add_view()
            case (_, "error"):
                self.handle_error_message()
            case (_, "category_editor"):
                return self.screen_triggers("category_editor_screen")
            case _:
                raise Exception(f"Unhandled display state {value}")

    def handle_app_play_state(self, _, value):
        self.play_state = value

    def handle_notes_display_view(self):
        ...

    def handle_pagination(
        self, _, value: tuple["PAGINATION_DIRECTION", "MarkdownNoteDict"]
    ):
        """
        We're given note_data to populate into notes and the desired transition



        Parameters
        ----------
        _
        value:
            direction : {-1, 0, 1}
                If -1, this data is dispatched to 'next' screen, and screen transition is reversed
                If 0, this data is dispatched to 'current' screen, and no screen transition occurs if current screen
                 is a note_screen.
                If 1,  this data is dispatched to 'next' screen, and screen transition is normal
            note_data : MarkdownNoteDict

        Returns
        -------

        """
        direction, note_data = value
        funcs = []
        match direction:
            case -1 | 1:
                Logger.info(f"{type(self).__name__}: handle_pagination - {direction}")
                self.reversed_transition = direction < 0
                target_screen = self.get_screen(
                    f"note_screen_{self.note_screen_cycler.next(peek=True)}"
                )
                advance_index = caller(self.note_screen_cycler, "next")
                funcs.append(advance_index)
            case 0:
                Logger.info(
                    f"{type(self).__name__}: handle_pagination - update current screen"
                )
                self.reversed_transition = False
                target_screen = self.get_screen(
                    f"note_screen_{self.note_screen_cycler.current}"
                )
            case _:
                raise NotImplementedError(f"Invalid direction {direction}")

        set_data = caller(target_screen, "set_note_content", note_data)
        trigger_screen_display = caller(self, "screen_triggers", target_screen.name)
        # Advance index

        sch_cb(set_data, trigger_screen_display, *funcs)
        return True

    def handle_notes_list_view(self, *_args):
        self.screen_triggers("list_view_screen")

    def handle_notes_edit_view(self, *_args):
        Logger.debug(f"{type(self).__name__} : Switching to note_edit_screen")
        self.screen_triggers("note_edit_screen")

    def handle_notes_add_view(self, *_args):
        Logger.debug(
            f"{type(self).__name__} : Switching to note_edit_screen - Adding Note"
        )
        self.screen_triggers("note_edit_screen")

    def handle_error_message(self, *_args):
        Logger.debug(f"{type(self).__name__} : Switching to error_message_screen")
        self.screen_triggers("error_message_screen")
