from typing import TYPE_CHECKING, Literal

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager

from mindref.lib.widgets.behavior import BackBehavior
from mindref.lib.widgets.refreshable import V2RefreshBehavior

if TYPE_CHECKING:
    from kivy.event import EventDispatcher
    from kivy.uix.widget import Widget

Builder.load_string(
    """
#:import SlideTransition kivy.uix.screenmanager.SlideTransition
#:import MainScreen mindref.screens.main_screen
#:import EditScreen mindref.screens.edit_screen
#:import DraftScreen mindref.screens.draft_screen

<NoteAppScreenManager>:
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

TScreenName = Literal["main_screen", "edit_screen", "draft_screen"]


class NoteAppScreenManager(V2RefreshBehavior, ScreenManager, BackBehavior):
    current: TScreenName

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        self.current = "main_screen"

    def on_back(self, source: "EventDispatcher") -> bool:
        """Offer the back action to the visible screen, and to nothing else"""
        screen = self.current_screen
        if screen is None or not screen.is_event_type("on_back"):
            return False
        return bool(screen.dispatch("on_back", source))

    def on_refresh(self, widget: "Widget", state: bool, to_children: bool) -> bool:
        Logger.debug(
            f"{type(self).__name__} : on_refresh called with src={widget}, {state=}, {to_children=}"
        )

        if to_children:
            for screen in self.screens:
                if screen.is_event_type("on_refresh"):
                    screen.dispatch("on_refresh", widget, state, to_children)
            return True

        return False
