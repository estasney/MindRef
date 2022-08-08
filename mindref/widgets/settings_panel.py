from kivy.factory import Factory
from kivy.uix.settings import SettingsWithSpinner

from widgets.behavior.interact_behavior import InteractBehavior


class MindRefSettings(InteractBehavior, SettingsWithSpinner):
    """Extends `SettingsWithSpinner` to fire the 'interact' event"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


Factory.register("MindRefSettings", cls=MindRefSettings)
