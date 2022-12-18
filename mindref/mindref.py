import json
from pathlib import Path
from typing import Callable, Literal, TYPE_CHECKING

from kivy import platform
from kivy._clock import ClockEvent  # noqa
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.config import Config
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.parser import parse_color
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)

from adapters.atlas.fs.fs_atlas_repository import AtlasService
from adapters.editor.fs.fs_editor_repository import FileSystemEditor
from adapters.notes.note_repository import NoteRepositoryFactory
from domain.events import (
    AddNoteEvent,
    BackButtonEvent,
    CancelEditEvent,
    DiscoverCategoryEvent,
    EditNoteEvent,
    ListViewButtonEvent,
    NoteCategoryEvent,
    NoteCategoryFailureEvent,
    NoteFetchedEvent,
    NotesQueryEvent,
    NotesQueryFailureEvent,
    PaginationEvent,
    RefreshNotesEvent,
    SaveNoteEvent,
    TypeAheadQueryEvent,
    FilePickerEvent,
    CreateCategoryEvent,
)
from domain.settings import app_settings
from plugins import PluginManager
from service.registry import Registry
from utils import attrsetter, caller, sch_cb, get_app
from utils.triggers import trigger_factory
from widgets.screens.manager import NoteAppScreenManager

if TYPE_CHECKING:
    DISPLAY_STATES = Literal[
        "choose", "display", "list", "edit", "add", "error", "category_editor"
    ]
    DISPLAY_STATE = tuple[DISPLAY_STATES, DISPLAY_STATES]
    PLAY_STATE = Literal["play", "pause"]


class MindRefApp(App):
    APP_NAME = "MindRef"
    atlas_service = AtlasService(storage_path=Path("./static").resolve())
    note_service = NoteRepositoryFactory.get_repo()(get_app=get_app, new_first=True)
    editor_service = FileSystemEditor(get_app=get_app)
    plugin_manager = PluginManager()
    platform_android = BooleanProperty(defaultvalue=False)
    registry = Registry()

    note_categories = ListProperty()
    note_category = StringProperty(allownone=True)
    note_category_meta = ListProperty()

    editor_note = ObjectProperty(allownone=True)

    menu_open = BooleanProperty(False)

    display_state_last = OptionProperty(
        "choose",
        options=[
            "choose",
            "display",
            "list",
            "edit",
            "add",
            "error",
            "category_editor",
        ],
    )
    display_state_current = OptionProperty(
        "choose",
        options=[
            "choose",
            "display",
            "list",
            "edit",
            "add",
            "error",
            "category_editor",
        ],
    )
    display_state_trigger: Callable[["DISPLAY_STATES"], None]

    play_state = OptionProperty("play", options=["play", "pause"])
    play_state_trigger: Callable[["PLAY_STATE"], None]

    error_message = StringProperty()

    paginate_interval = NumericProperty(15)
    paginate_timer: ClockEvent

    screen_manager = ObjectProperty()

    fonts = DictProperty({"mono": "RobotoMono", "default": "Roboto"})
    base_font_size = NumericProperty()
    colors = DictProperty(
        {
            "White": (1, 1, 1),
            "Gray-100": parse_color("#f3f3f3"),
            "Gray-200": parse_color("#dddedf"),
            "Gray-300": parse_color("#c7c8ca"),
            "Gray-400": parse_color("#9a9da1"),  # White text
            "Gray-500": parse_color("#6d7278"),
            "Codespan": parse_color("#00000026"),
            "Keyboard": parse_color("#c4c4c4"),
            "KeyboardShadow": parse_color("#656565"),
            "Primary": parse_color("#37464f"),
            "Dark": parse_color("#101f27"),
            "Accent-One": parse_color("#388fe5"),
            "Accent-Two": parse_color("#56e39f"),
            "Warn": parse_color("#fa1919"),
        }
    )
    """
        Attributes
        ----------

        note_service: AbstractNoteRepository
        note_categories: ListProperty
            All known note categories
        note_category: StringProperty
            The active Category. If no active category, value is empty string
        editor_note: ObjectProperty
            Ephemeral note used by editor service
        note_category_meta: ListProperty
            Metadata for notes associated with active Category. Info such as Title and index
        next_note_scheduler: ObjectProperty
        current_display_state: OptionProperty
            One of ["choose", "display", "list", "edit", "add", "error"]
                - choose: Display all known categories
                - display: Iterate through notes matching `self.note_category`
                - list: show a listing of notes in self.note_category
                - edit: Open an editor for current note
                - add: Open an editor for a new note
                - error: Show an error screen
        error_message: StringProperty
            Message 
        play_state: OptionProperty
            One of [play, pause]
            play:: schedule pagination through notes
            pause:: stop pagination through notes
        screen_manager: ObjectProperty
            Holds the reference to ScreenManager
        colors: DictProperty
            Color scheme
        log_level: NumericProperty
        """

    settings_cls = "MindRefSettings"

    def get_display_state(self):
        return self.display_state_last, self.display_state_current

    def set_display_state(self, value: "DISPLAY_STATES"):
        self.display_state_last = self.display_state_current
        self.display_state_current = value

    display_state = AliasProperty(
        get_display_state,
        set_display_state,
        bind=("display_state_last", "display_state_current"),
        cache=True,
    )

    def on_display_state(self, _, value: "DISPLAY_STATE"):
        old, new = value
        match (old, new):
            case _, "edit":
                self.editor_note = self.editor_service.edit_current_note()
                self.play_state_trigger("pause")
            case _, "add":
                self.editor_note = self.editor_service.new_note(
                    category=self.note_category, idx=self.note_service.index_size()
                )
                self.play_state_trigger("pause")

    def on_play_state(self, *_args):
        if self.play_state == "pause":
            self.paginate_timer.cancel()
        else:
            self.paginate_timer()

    def on_paginate_interval(self, *_args):
        """Interval for Autoplay has changed"""
        self.paginate_timer.cancel()
        pagination = caller(self, "paginate_note", direction=1)
        self.paginate_timer = Clock.create_trigger(
            pagination,
            timeout=self.paginate_interval,
            interval=True,
        )
        if self.play_state == "play":
            self.paginate_timer()

    def on_paginate(self, *args, **kwargs):
        ...

    def select_index(self, value: int):
        self.registry.set_note_index(value)

    def paginate(self, value):
        paginate = caller(self, "paginate_note", direction=value)
        if self.play_state == "play":
            self.paginate_timer.cancel()

            setup_timer = caller(self, "paginate_timer")
            sch_cb(paginate, setup_timer, timeout=0.1)
        else:
            sch_cb(paginate, timeout=0.1)

    def paginate_note(self, direction=1):
        """
        Update our note_data, and the direction transition for our ScreenManager
        """

        return self.registry.paginate_note(direction)

    @mainthread
    def process_event(self, *_args):
        """Pop an Event from Registry and Process"""
        registry = self.registry
        if len(registry.events) == 0:
            return
        event = registry.events.popleft()
        Logger.debug(f"Processing Event: {type(event).__name__}")
        match event:
            case TypeAheadQueryEvent(query=query, on_complete=on_complete):
                return registry.query_category(
                    category=self.note_category,
                    query=query,
                    on_complete=on_complete,
                )
            case DiscoverCategoryEvent(category=category):
                if category not in self.note_categories:
                    Logger.info(
                        f"{type(self).__name__}: Found New Category - {event!r}"
                    )
                    self.note_categories.append(category)
                return
            case BackButtonEvent(display_state=(old, new)):
                match (old, new):
                    case _, "choose":
                        # Cannot go further back
                        Logger.info(
                            f"{type(self).__name__}: process_back_button_event: Exiting"
                        )
                        get_app().stop()
                    case _, "display":
                        clear_registry_category = caller(
                            registry,
                            "set_note_category",
                            value=None,
                            on_complete=None,
                        )
                        trigger_display_choose = caller(
                            self, "display_state_trigger", "choose"
                        )
                        sch_cb(clear_registry_category, trigger_display_choose)
                        Logger.info(
                            f"{type(self).__name__}: process_back_button_event - scheduled display_state: choose"
                        )
                    case _, "list":
                        trigger_display = caller(
                            self, "display_state_trigger", "display"
                        )
                        sch_cb(trigger_display)
                        Logger.info(
                            f"{type(self).__name__}: process_back_button_event - scheduled display_state: display"
                        )
                    case _, "edit" | "add":
                        registry.push_event(CancelEditEvent())
                    case previous, "category_editor":
                        self.display_state_trigger(previous)
                    case _:
                        Logger.warning(
                            f"Unknown display state encountered when handling back button: {old},{new}"
                        )
                return
            case NotesQueryFailureEvent(
                error=error, message=message, on_complete=on_complete
            ):
                if on_complete is not None:
                    sch_cb(on_complete)

                match error:
                    case "permission_error" | "not_found":
                        self.note_service.storage_path = None
                        app_config = Config.get_configparser("app")
                        app_config.set("Storage", "NOTES_PATH", App.user_data_dir)
                        app_config.write()

                match (error, platform):
                    case ("permission_error", "android"):
                        return registry.push_event(
                            FilePickerEvent(
                                on_complete=None,
                                action=FilePickerEvent.Action.OPEN_FOLDER,
                            )
                        )
                    case _:
                        self.error_message = message
                        self.display_state_trigger("error")

            case NotesQueryEvent(on_complete=on_complete):
                if on_complete:
                    sch_cb(on_complete, timeout=0.1)
                return self.screen_manager.dispatch("on_refresh", False)

            case NoteCategoryFailureEvent(value=value):
                Logger.error(event)
                if self.config.get("Behavior", "CATEGORY_SELECTED") == value:
                    # Clear the config
                    app_config = Config.get_configparser("app")
                    app_config.set("Behavior", "CATEGORY_SELECTED", "")
                    app_config.write()
                self.paginate_timer.cancel()
                # We'll get another event to clear app's note category
                return registry.set_note_category(None, on_complete=None)
            case NoteCategoryEvent(value=value):
                """
                Note Category has been set via registry. If a valid string, we need to query and set category_meta.
                Otherwise, if None, we clear it
                """
                set_note_category = attrsetter(self, "note_category", value)
                match value:
                    case str():

                        def set_note_category_meta(meta):
                            self.note_category_meta = meta
                            sch_cb(
                                set_note_category,
                                refresh_note_page,
                                trigger_display_state,
                                timeout=0.1,
                            )

                        # Query Category Meta, on_complete - Set App note_category_meta to result
                        get_category_meta = caller(
                            self.note_service,
                            "get_category_meta",
                            category=value,
                            on_complete=set_note_category_meta,
                        )

                        # Paginate the note
                        refresh_note_page = caller(self, "paginate_note", direction=0)

                        # Display the notes
                        trigger_display_state = caller(
                            self, "display_state_trigger", "display"
                        )

                        sch_cb(get_category_meta, timeout=0.1)
                        Logger.info(
                            f"{type(self).__name__}: process_note_category_event - Scheduled Updating Note Data"
                        )
                    case None:
                        clear_note_meta = attrsetter(self, "note_category_meta", [])
                        sch_cb(set_note_category, clear_note_meta)
                        Logger.info(
                            f"{type(self).__name__}: process_note_category_event - Scheduled Clearing Note Data"
                        )
                    case _:
                        raise AssertionError(f"Unhandled {event!r}.value : {value}")
                return
            case ListViewButtonEvent():
                """List Button was Pressed"""
                return self.display_state_trigger("list")
            case RefreshNotesEvent(on_complete=on_complete):
                clear_categories = attrsetter(self, "note_categories", [])
                clear_caches = caller(registry, "clear_caches")
                run_query = caller(registry, "query_all", on_complete=on_complete)
                return sch_cb(clear_categories, clear_caches, run_query, timeout=0.5)
            case NoteFetchedEvent(note=note):
                update_data = attrsetter(self, "note_data", note.to_dict())
                refresh_note = caller(self, "paginate_note", direction=0)
                return sch_cb(update_data, refresh_note, timeout=0.1)
            case SaveNoteEvent(text=text, title=title):
                """Save Button Pressed in Editor"""
                note_is_new = self.display_state_current == "add"
                data_note = self.editor_note
                data_note.edit_text = text
                if note_is_new:
                    data_note.edit_title = title
                remove_edit_note_widget = attrsetter(self, "editor_note", None)
                persist_note = caller(registry, "save_note", note=data_note)
                return sch_cb(persist_note, remove_edit_note_widget, timeout=0.1)
            case AddNoteEvent():
                data_note = registry.new_note(category=self.note_category, idx=None)
                add_edit_note_widget = attrsetter(self, "editor_note", data_note)
                trigger_display_add = caller(self, "display_state_trigger", "add")
                return sch_cb(add_edit_note_widget, trigger_display_add, timeout=0.1)
            case EditNoteEvent(category=category, idx=idx):
                data_note = registry.edit_note(category=category, idx=idx)
                add_edit_note_widget = attrsetter(self, "editor_note", data_note)
                trigger_display_edit = caller(self, "display_state_trigger", "edit")
                return sch_cb(add_edit_note_widget, trigger_display_edit, timeout=0.1)
            case CancelEditEvent():
                trigger_display = caller(self, "display_state_trigger", "display")
                registry_paginate = caller(registry, "paginate_note", direction=0)
                remove_edit_note = attrsetter(self, "editor_note", None)
                return sch_cb(
                    trigger_display, registry_paginate, remove_edit_note, timeout=0.1
                )
            case PaginationEvent(direction=direction):
                registry_paginate = caller(
                    registry, "paginate_note", direction=direction
                )
                return Clock.schedule_once(registry_paginate)
            case FilePickerEvent() as pick_event:
                return self.registry.handle_picker_event(pick_event)

            case CreateCategoryEvent(
                action=action, category=category, img_path=img_path
            ) as event:
                event_action = event.Action
                match action, category, img_path:
                    case event_action.OPEN_FORM, _, _:
                        return self.display_state_trigger("category_editor")
                    case event_action.CLOSE_FORM | event_action.CLOSE_REJECT, _, _:
                        return self.display_state_trigger(self.display_state_last)
                    case event_action.CLOSE_ACCEPT, str(category), img_path:
                        Logger.info(
                            f"{type(self).__name__}: process_event - Create Category {category}"
                        )
                        return self.display_state_trigger(self.display_state_last)

            case _:
                Logger.info(
                    f"{type(self).__name__}: process_event - Unhandled Event {type(event).__name__}"
                )
                return

    def key_input(self, _window, key, _scancode, _codepoint, _modifier):
        if key == 27:  # Esc Key
            # Back Button Event
            self.registry.push_event(BackButtonEvent(display_state=self.display_state))
            return True
        else:
            return False

    """Kivy"""

    def build(self):
        truthy = {True, 1, "1", "True"}
        # noinspection PyUnresolvedReferences
        self.register_event_type("on_paginate")
        self.platform_android = platform == "android"
        self.registry.app = self
        self.play_state_trigger = trigger_factory(
            self, "play_state", self.__class__.play_state.options
        )
        self.display_state_trigger = trigger_factory(
            self, "display_state", self.__class__.display_state_current.options
        )
        self.paginate_timer = Clock.create_trigger(
            self.paginate_note, timeout=self.paginate_interval, interval=True
        )
        Window.bind(on_keyboard=self.key_input)
        storage_path = (
            np if (np := self.config.get("Storage", "NOTES_PATH")) != "None" else None
        )

        if storage_path:
            self.registry.set_note_storage_path(storage_path)
        self.note_service.new_first = (
            True if self.config.get("Behavior", "NEW_FIRST") in truthy else False
        )
        sm = NoteAppScreenManager()
        self.screen_manager = sm
        self.play_state = (
            "play" if self.config.get("Behavior", "PLAY_STATE") in truthy else "pause"
        )
        # Invokes note_service.discover_notes
        self.registry.query_all()

        self.base_font_size = self.config.get("Display", "BASE_FONT_SIZE")
        Clock.schedule_interval(self.process_event, 0.1)
        self.plugin_manager.init_app(self)
        sm.fbind(
            "on_interact", lambda x: self.plugin_manager.plugin_event("on_interact")
        )

        return sm

    def build_settings(self, settings):
        settings.add_json_panel("MindRef", self.config, data=json.dumps(app_settings))

    def build_config(self, config):
        match platform:  # We can't use self.platform_android yet
            case "android":
                config.setdefaults("Storage", {"NOTES_PATH": None})
                config.setdefaults("Display", {"BASE_FONT_SIZE": 18})
                config.setdefaults(
                    "Behavior",
                    {
                        "NEW_FIRST": True,
                        "PLAY_STATE": False,
                        "PLAY_DELAY": 15,
                        "CATEGORY_SELECTED": "",
                    },
                )
                config.setdefaults(
                    "Plugins", {"SCREEN_SAVER_ENABLE": False, "SCREEN_SAVER_DELAY": 60}
                )

            case _:
                config.setdefaults(
                    "Storage",
                    {"NOTES_PATH": self.user_data_dir},
                )
                config.setdefaults("Display", {"BASE_FONT_SIZE": 16})
                config.setdefaults(
                    "Behavior",
                    {
                        "NEW_FIRST": True,
                        "PLAY_STATE": False,
                        "PLAY_DELAY": 15,
                        "CATEGORY_SELECTED": "",
                    },
                )
                config.setdefaults(
                    "Plugins", {"SCREEN_SAVER_ENABLE": False, "SCREEN_SAVER_DELAY": 60}
                )

    def on_config_change(self, config, section, key, value):

        truthy = {True, 1, "1", "True"}
        Logger.info(f"{type(self).__name__}: on_config_change - {section},{key}")
        match section, key:
            case "Storage", "NOTES_PATH" if not self.platform_android:
                self.note_service.storage_path = value
                self.display_state_trigger("choose")
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Storage", "NOTES_PATH" if self.platform_android:
                self.registry.set_note_storage_path(value)
                self.display_state_trigger("choose")
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "NEW_FIRST":
                self.note_service.new_first = True if value in truthy else False
                self.display_state_trigger("choose")
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "PLAY_STATE":
                ...  # No effect here, this is on first load
            case "Behavior", "PLAY_DELAY":
                self.paginate_interval = int(value)
            case "Display", "BASE_FONT_SIZE":
                self.base_font_size = int(value)
            case "Plugins", _:
                ...


if __name__ == "__main__":
    MindRefApp().run()
