from typing import Literal

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.widget import Widget

from mindref.lib.widgets.refreshable import V2RefreshBehavior

Builder.load_string(
    """
#:import SlideTransition kivy.uix.screenmanager.SlideTransition
#:import MainScreen mindref.screens.main_screen
#:import EditScreen mindref.screens.edit_screen
#:import DraftScreen mindref.screens.draft_screen

<NoteAppScreenManager>:
    id: screen_manager
    app: app
    transition: SlideTransition()
    MainScreen:
        id: main_screen
        name: 'main_screen'
    EditScreen:
        id: edit_screen
        name: 'edit_screen'
    DraftScreen:
        id: draft_screen
        name: 'draft_screen'
"""
)

TScreenNames = Literal["main_screen", "edit_screen", "draft_screen"]


class NoteAppScreenManager(V2RefreshBehavior, ScreenManager):
    app = ObjectProperty()
    current: TScreenNames

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current = "main_screen"

    def on_refresh(self, widget: "Widget", state: bool, to_children: bool):
        Logger.debug(
            f"{type(self).__name__} : on_refresh called with src={widget}, {state=}, {to_children=}"
        )

        if to_children:
            for screen in self.screens:
                if screen.is_event_type("on_refresh"):
                    screen.dispatch("on_refresh", widget, state, to_children)
            return True

        return False
