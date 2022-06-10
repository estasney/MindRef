from itertools import cycle
from typing import Literal, TYPE_CHECKING

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    BoundedNumericProperty,
    ListProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)

from kivy.uix.screenmanager import (
    CardTransition,
    FadeTransition,
    RiseInTransition,
    Screen,
    ScreenManager,
    SlideTransition,
    SwapTransition,
    WipeTransition,
)

from toolz import sliding_window

from utils import import_kv, sch_cb
from widgets.app_menu import AppMenu
from widgets.effects.scrolling import RefreshSymbol

TR_OPTS = Literal["None", "Slide", "Rise-In", "Card", "Fade", "Swap", "Wipe"]

if TYPE_CHECKING:
    from widgets.categories import NoteCategoryButton
    from services.domain import MarkdownNoteDict, MarkdownNote
    from kivy.uix.codeinput import CodeInput

import_kv(__file__)


class NoteAppScreenManager(ScreenManager):
    app = ObjectProperty()
    play_state = StringProperty()
    screen_transitions = OptionProperty(
        "slide", options=["None", "Slide", "Rise-In", "Card", "Fade", "Swap", "Wipe"]
    )
    menu_open = BooleanProperty(False)
    n_screens = BoundedNumericProperty(defaultvalue=2, min=1, max=2)

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.current = "chooser_screen"
        self.note_screen_cycler = None
        self.make_note_cycler()
        self.last_note_screen = None
        self.app = app
        self.menu = None
        app.bind(display_state=self.handle_app_display_state)
        app.bind(play_state=self.setter("play_state"))
        app.bind(screen_transitions=self.setter("screen_transitions"))
        app.bind(menu_open=self.setter("menu_open"))
        self.fbind("n_screens", self.handle_n_screens)
        self.fbind("menu_open", self.handle_menu_state)

    def make_note_cycler(self):
        for i in range(self.n_screens):
            note_screen = NoteCategoryScreen(name=f"note_screen{i}")
            self.add_widget(note_screen)
        self.note_screen_cycler = sliding_window(2, cycle(range(self.n_screens)))

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

    def handle_n_screens(self, instance, value):
        self.clear_widgets()
        self.make_note_cycler()

    def category_selected(self, category: "NoteCategoryButton"):
        self.app.note_category = category.text

    def on_screen_transitions(self, instance, value: TR_OPTS):
        if value == "None":
            self.n_screens = 1
            return True
        elif value == "Slide":
            self.transition = SlideTransition()
            return True
        elif value == "Rise-In":
            self.transition = RiseInTransition()
            return True
        elif value == "Card":
            self.transition = CardTransition()
            return True
        elif value == "Fade":
            self.transition = FadeTransition()
            return True
        elif value == "Swap":
            self.transition = SwapTransition()
            return True
        elif value == "Wipe":
            self.transition = WipeTransition()
            return True
        else:
            raise ValueError(f"Unhandled Transition {value}")

    def handle_app_display_state(self, instance, new):
        Logger.debug(f"ScreenManager: app_display_state : {new}")
        if new == "choose":  # Show the Category Selection Screen
            self.current = "chooser_screen"
        elif new == "display":
            self.handle_notes()
        elif new == "list":
            self.handle_notes_list_view()
        elif new == "edit":
            self.handle_notes_edit_view()

        else:
            raise Exception(f"Unhandled display state {new}")

    def handle_app_play_state(self, instance, value):
        self.play_state = value

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

    def handle_notes_edit_view(self, *args, **kwargs):
        Logger.debug("Switching to edit view")
        fs = self.app.editor_service
        edit_note = fs.edit_current_note(self.app)
        edit_screen: "NoteEditScreen" = self.ids["note_edit_screen"]
        update_screen = lambda x: setattr(self, "current", "note_edit_screen")
        set_init_text = lambda x: setattr(edit_screen, "init_text", edit_note.edit_text)
        sch_cb(0, update_screen, set_init_text)


class NoteCategoryChooserScreen(Screen):
    chooser = ObjectProperty()
    categories = ListProperty()
    refresh_triggered = BooleanProperty(False)
    refresh_running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_icon = None
        self.fbind("refresh_running", self.handle_refresh_running)

    def category_selected(self, category_btn: "NoteCategoryButton"):
        self.manager.category_selected(category_btn)

    def handle_refresh_icon(self, dt):
        """
        Child can notify us to display refresh icon but we want to handle it's clearing
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

    def clear_refresh_icon(self, instance, value):
        Logger.debug("Clearing Refresh Icon")
        self.unbind(categories=self.clear_refresh_icon)
        if self.refresh_icon:
            self.remove_widget(self.refresh_icon)
            del self.refresh_icon
            self.refresh_icon = None
        self.refresh_running = False

    def handle_refresh_running(self, instance, value):
        """Call the NoteService and ask for refresh"""
        Logger.debug("Refreshing")
        app = App.get_running_app()
        self.bind(categories=self.clear_refresh_icon)
        Clock.schedule_once(app.refresh_note_categories, 1)

    def on_refresh_triggered(self, instance, value):
        Clock.schedule_once(self.handle_refresh_icon)


class NoteCategoryScreen(Screen):
    current_note = ObjectProperty()

    def set_note_content(self, note_data: "MarkdownNoteDict"):
        self.current_note.set_note_content(note_data)


class NoteListViewScreen(Screen):
    meta_notes = ListProperty()

    def set_note_list_view(self, *args, **kwargs):
        Clock.schedule_once(lambda dt: self.ids["scroller"].set(self.meta_notes), 0)


class NoteEditScreen(Screen):
    from pygments.lexers import get_lexer_by_name

    editor = ObjectProperty()
    init_text = StringProperty()
    lexer = ObjectProperty(get_lexer_by_name("Markdown"))
    style_name = StringProperty("paraiso-dark")

    def __init__(self, **kwargs):
        super(NoteEditScreen, self).__init__(**kwargs)
        self.fbind("init_text", self.handle_init_text)

    def handle_init_text(self, instance, value):
        editor: "CodeInput" = self.editor
        editor.text = self.init_text

    def handle_save(self):
        Logger.debug("Saving Note")
        # Store new text to memory - we want to close the editor screen ASAP

        app = App.get_running_app()

        from utils.registry import app_registry

        app_registry.note_editor.notify("edit", text=self.editor.text)
        md_note = None

        def md_save_cb(md):
            """Registry can't directly return a value, but can call a function with result"""
            nonlocal md_note
            md_note = md

        app_registry.note_editor.notify("save", cb=md_save_cb)

        # noinspection PyUnresolvedReferences
        app.note_data = md_note.to_dict()
        update_display_state = lambda x: setattr(app, "display_state", "display")
        clear_self_text = lambda x: setattr(self, "init_text", "")

        sch_cb(0, update_display_state, clear_self_text)

    def handle_cancel(self, *args, **kwargs):
        Logger.debug("Cancel Edit")
        from utils.registry import app_registry

        app_registry.note_editor.notify("cancel")
        app = App.get_running_app()

        update_display_state = lambda x: setattr(app, "display_state", "display")
        clear_self_text = lambda x: setattr(self, "init_text", "")

        sch_cb(0, update_display_state, clear_self_text)
