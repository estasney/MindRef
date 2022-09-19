from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.scrollview import ScrollView

from domain.events import RefreshNotesEvent
from utils import import_kv
from widgets.buttons.category import NoteCategoryButton
from widgets.effects.scrolling import RefreshOverscrollEffect, RefreshSymbol
from widgets.screens import InteractScreen

import_kv(__file__)


class NoteCategoryChooserScreen(InteractScreen):
    chooser = ObjectProperty()
    refresh_triggered = BooleanProperty(False)
    refresh_running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_icon = None
        self.handle_refresh_running_trigger = Clock.create_trigger(
            self.handle_refresh_running
        )
        self.fbind("refresh_running", self.handle_refresh_running_trigger)

    def category_selected(self, category_btn: "NoteCategoryButton"):
        self.manager.category_selected(category_btn)

    def handle_refresh_icon(self, dt):
        """
        Child can notify us to display refresh icon, but screen will control when it clears
        """
        if (
            self.refresh_triggered
            and not self.refresh_icon
            and not self.refresh_running
        ):
            self.refresh_running = True
            self.refresh_icon = RefreshSymbol(
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )
            self.add_widget(self.refresh_icon)

    def clear_refresh_icon(self, *args, **kwargs):
        if self.refresh_icon:
            self.remove_widget(self.refresh_icon)
            del self.refresh_icon
            self.refresh_icon = None
        self.refresh_running = False

    def handle_refresh_running(self, *args):
        """Call the NoteService and ask for refresh"""
        if self.refresh_running:
            Logger.info("Refreshing")
            app = App.get_running_app()
            app.registry.push_event(
                RefreshNotesEvent(on_complete=self.clear_refresh_icon)
            )

    def on_refresh_triggered(self, instance, value):
        Clock.schedule_once(self.handle_refresh_icon)


class CategoryScreenScrollWrapper(ScrollView):
    """Screen With Buttons for Categories"""

    screen = ObjectProperty()
    chooser = ObjectProperty()
    refresh_triggered = BooleanProperty(False)

    effect_cls = RefreshOverscrollEffect

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_chooser(self, instance, value):
        self.chooser.bind(minimum_height=self.chooser.setter("height"))

    def on_screen(self, instance, value):
        self.bind(refresh_triggered=self.screen.setter("refresh_triggered"))

    def category_selected(self, instance: "NoteCategoryButton"):
        self.screen.category_selected(instance)
