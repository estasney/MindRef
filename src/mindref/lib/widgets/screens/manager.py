from kivy import Logger
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager

from mindref.lib.widgets.behavior.interact_behavior import InteractBehavior
from mindref.lib.widgets.behavior.refresh_behavior import RefreshBehavior

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


class NoteAppScreenManager(InteractBehavior, RefreshBehavior, ScreenManager):
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current = "main_screen"

    def on_refresh(self, state: bool):
        Logger.info(f"{type(self).__name__} : on_refresh called with state={state}")
        self.dispatch_children(self, "on_refresh", state)
        return True
