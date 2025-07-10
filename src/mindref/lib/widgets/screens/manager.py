from kivy import Logger
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager

from mindref.lib.widgets.behavior.interact_behavior import InteractBehavior
from mindref.lib.widgets.refreshable import V2RefreshBehavior

Builder.load_string(
    """
#:import SlideTransition kivy.uix.screenmanager.SlideTransition
#:import MainScreen mindref.lib.widgets.screens.main_screen.MainScreen

<NoteAppScreenManager>:
    id: screen_manager
    app: app
    transition: SlideTransition()
    MainScreen:
        id: main_screen
        name: 'main_screen'
"""
)


class NoteAppScreenManager(InteractBehavior, V2RefreshBehavior, ScreenManager):
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current = "main_screen"

    def on_refresh(self, widget, state: bool, to_children: bool):
        Logger.debug(
            f"{type(self).__name__} : on_refresh called with src={widget}, {state=}, {to_children=}"
        )

        if to_children:
            return self.current_screen.dispatch(
                "on_refresh", widget, state, to_children
            )

        return False
