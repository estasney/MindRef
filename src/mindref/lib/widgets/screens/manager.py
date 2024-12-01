from collections.abc import Callable
from typing import TYPE_CHECKING

from kivy import Logger
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from lib.domain.events import FilePickerEvent
from lib.utils import import_kv, sch_cb, schedulable
from lib.utils.index import RollingIndex
from lib.utils.triggers import trigger_factory
from lib.widgets.app_menu.app_menu import AppMenu
from lib.widgets.behavior.interact_behavior import InteractBehavior
from lib.widgets.behavior.refresh_behavior import RefreshBehavior
from lib.widgets.buttons.category import NoteCategoryButton
from lib.widgets.dialog.filepicker_dialog import LoadDialog
from lib.widgets.editor.category_editor import CategoryEditor

if TYPE_CHECKING:

    from lib.domain.events import PAGINATION_DIRECTION
    from lib.domain.markdown_note import MarkdownNoteDict

import_kv(__file__)


class NoteAppScreenManager(InteractBehavior, RefreshBehavior, ScreenManager):
    app = ObjectProperty()
    popup = ObjectProperty(None, allownone=True)
    drawer_cls = ObjectProperty()
    drawer = ObjectProperty(None, allownone=True)
    menu_open = BooleanProperty(False)
    reversed_transition = BooleanProperty(False)
    screen_triggers: Callable[[str], None]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_screen_cycler = RollingIndex(size=2)
        self.current = "chooser_screen"
        self.app.bind(display_state=self.handle_app_display_state)
        self.app.bind(on_paginate=self.handle_pagination)
        self.app.bind(menu_open=self.setter("menu_open"))
        self.fbind("menu_open", self.handle_menu_state)
        self.fbind("reversed_transition", self.handle_reversed_transition)
        self.screen_triggers = trigger_factory(self, "current", self.screen_names)
        self.drawer = self.drawer_cls(size_hint=(0.3, 1))
        self.drawer.bind(on_close=lambda *_: setattr(self.app, "menu_open", False))

    def on_refresh(self, state: bool):
        self.dispatch_children("on_refresh", state)
        return True

    def handle_menu_state(self, _, menu_open: bool):
        if menu_open:
            view = AppMenu()
            self.drawer.content = view
            self.drawer.open()
            view.fbind("on_dismiss", self.drawer.close)

        elif not menu_open and self.drawer:
            self.drawer.close()

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
                # return self.screen_triggers("category_editor_screen")
                # Attach a CategoryEditor to the ScreenContainer
                container_screen = next(
                    (
                        screen
                        for screen in self.screens
                        if screen.name == "screen_container"
                    ),
                    None,
                )
                if not container_screen:
                    raise ValueError("No Screen Container Found")
                container_screen.content = CategoryEditor()
                trigger_screen = schedulable(self.screen_triggers, "screen_container")
                sch_cb(trigger_screen, timeout=0.1)
            case _:
                raise Exception(f"Unhandled display state {value}")

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
                advance_index = schedulable(self.note_screen_cycler.next)
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

        set_data = schedulable(target_screen.set_note_content, note_data)
        trigger_screen_display = schedulable(self.screen_triggers, target_screen.name)
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

    def open_file_picker(self, event: FilePickerEvent):
        action = event.Action

        match event:
            case FilePickerEvent(
                action=action.OPEN_FOLDER | action.OPEN_FILE as event_action,
                ext_filter=list() | None as ext_filter,
                on_complete=on_complete,
                start_folder=start_folder,
            ):
                self.popup = Popup(title="Select File")

                def dismiss_and_dispatch(val):
                    self.popup.dismiss()
                    on_complete(val)

                dialog = LoadDialog(
                    filters=ext_filter,
                    on_cancel=self.popup.dismiss,
                    on_accept=dismiss_and_dispatch,
                    dirselect=action.FOLDER in event_action,
                    start_folder=start_folder,
                )

                self.popup.content = dialog

        self.popup.open()
