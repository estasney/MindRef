import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from kivy import platform
from kivy._clock import ClockEvent  # noqa
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config, ConfigParser
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
from kivy.uix.settings import Settings

from mindref.lib import DisplayState
from mindref.lib.adapters.atlas import AtlasService
from mindref.lib.adapters.editor import FileSystemEditor
from mindref.lib.adapters.notes import NoteRepositoryFactory
from mindref.lib.domain.events import (
    AddNoteEvent,
    BackButtonEvent,
    CancelEditEvent,
    CreateCategoryEvent,
    DiscoverCategoryEvent,
    EditNoteEvent,
    FilePickerEvent,
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
)
from mindref.lib.domain.settings import app_settings
from mindref.lib.plugins import PluginManager
from mindref.lib.service import Registry
from mindref.lib.utils import attrsetter, get_app, sch_cb, schedulable, trigger_factory
from mindref.lib.widgets.screens.manager import NoteAppScreenManager


class MindRefApp(App):
    title = "MindRef"
    atlas_service = AtlasService(storage_path=Path(__file__).parent / "static")
    note_service = NoteRepositoryFactory.get_repo()(get_app=get_app)
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
        options=list(DisplayState),
        defaultvalue=DisplayState.CHOOSE.value,
    )
    display_state_current = OptionProperty(
        options=list(DisplayState),
        defaultvalue=DisplayState.CHOOSE.value,
    )
    display_state_trigger: Callable[[DisplayState], None]

    error_message = StringProperty()

    screen_manager = ObjectProperty()

    fonts = DictProperty({"mono": "RobotoMono", "default": "Roboto", "icons": "Icon"})
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
            "Keyboard": parse_color("#ffffffaf"),
            "KeyboardShadow": parse_color("#656565ff"),
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
        
        screen_manager: ObjectProperty
            Holds the reference to ScreenManager
        colors: DictProperty
            Color scheme
        log_level: NumericProperty
        """

    settings_cls = "MindRefSettings"

    def get_display_state(self) -> tuple[DisplayState, DisplayState]:
        return self.display_state_last, self.display_state_current

    def set_display_state(self, value: DisplayState) -> None:
        self.display_state_last = self.display_state_current
        self.display_state_current = value

    display_state = AliasProperty(
        get_display_state,
        set_display_state,
        bind=("display_state_current",),
        cache=True,
    )

    def on_display_state(self, _: Any, value: DisplayState) -> None:
        old, new = value
        match (old, new):
            case _, DisplayState.EDIT:
                self.editor_note = self.editor_service.edit_current_note()

            case _, DisplayState.ADD:
                self.editor_note = self.editor_service.new_note(
                    category=self.note_category, idx=self.note_service.index_size()
                )

    def on_paginate(self, *args, **kwargs) -> None: ...

    def select_index(self, value: int):
        self.registry.set_note_index(value)

    def paginate_note(self, direction: int = 1):
        """
        Update our note_data, and the direction transition for our ScreenManager
        """

        return self.registry.paginate_note(direction)

    def process_event(self, *_args):
        """Pop an Event from Registry and Process"""
        registry = self.registry
        if len(registry.events) == 0:
            return None
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
                return None
            case BackButtonEvent(display_state=(old, new)):
                match (old, new):
                    case _, DisplayState.CHOOSE:
                        # Cannot go further back
                        Logger.info(
                            f"{type(self).__name__}: process_back_button_event: Exiting"
                        )
                        get_app().stop()
                    case _, DisplayState.DISPLAY:
                        clear_registry_category = schedulable(
                            registry.set_note_category, value=None, on_complete=None
                        )
                        trigger_display_choose = schedulable(
                            self.display_state_trigger, DisplayState.CHOOSE
                        )
                        sch_cb(clear_registry_category, trigger_display_choose)
                        Logger.info(
                            f"{type(self).__name__}: process_back_button_event - scheduled display_state: {DisplayState.CHOOSE}"
                        )
                    case _, DisplayState.LIST:
                        trigger_display = schedulable(
                            self.display_state_trigger, DisplayState.DISPLAY
                        )
                        sch_cb(trigger_display)
                        Logger.info(
                            f"{type(self).__name__}: process_back_button_event - scheduled display_state: {DisplayState.DISPLAY}"
                        )
                    case _, DisplayState.EDIT | DisplayState.ADD:
                        registry.push_event(CancelEditEvent())
                    case previous, DisplayState.CATEGORY_EDITOR:
                        self.display_state_trigger(previous)
                    case _:
                        Logger.warning(
                            f"Unknown display state encountered when handling back button: {old},{new}"
                        )
                return None
            case NotesQueryFailureEvent(
                error=error, message=message, on_complete=on_complete
            ):
                if on_complete is not None:
                    sch_cb(on_complete)

                match error:
                    case "permission_error" | "not_found":
                        self.note_service.storage_path = None
                        app_config: ConfigParser | None = Config.get_configparser("app")
                        if app_config:
                            app_config.set(
                                "Storage", "NOTES_PATH", str(App.user_data_dir)
                            )
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
                        self.display_state_trigger(DisplayState.ERROR)
                        return None

            case NotesQueryEvent(on_complete=on_complete):
                if on_complete:
                    sch_cb(on_complete, timeout=0.1)
                return self.screen_manager.dispatch("on_refresh", False)

            case NoteCategoryFailureEvent(value=value):
                Logger.error(event)
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

                        get_category_meta = schedulable(
                            self.note_service.get_category_meta,
                            category=value,
                            on_complete=set_note_category_meta,
                            refresh=False,
                        )

                        # Paginate the note
                        refresh_note_page = schedulable(self.paginate_note, direction=0)

                        # Display the notes
                        trigger_display_state = schedulable(
                            self.display_state_trigger, DisplayState.DISPLAY
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
                return None
            case ListViewButtonEvent():
                """List Button was Pressed"""
                return self.display_state_trigger("list")
            case RefreshNotesEvent(on_complete=on_complete):
                clear_categories = attrsetter(self, "note_categories", [])
                clear_caches = schedulable(registry.clear_caches)
                run_query = schedulable(registry.query_all, on_complete=on_complete)
                return sch_cb(clear_categories, clear_caches, run_query, timeout=0.5)
            case NoteFetchedEvent(note=note):
                update_data = attrsetter(self, "note_data", note.to_dict())
                refresh_note = schedulable(self.paginate_note, direction=0)
                return sch_cb(update_data, refresh_note, timeout=0.1)
            case SaveNoteEvent(text=text, title=title):
                """Save Button Pressed in Editor"""
                note_is_new = self.display_state_current == "add"
                data_note = self.editor_note
                data_note.edit_text = text
                if note_is_new:
                    data_note.edit_title = title
                remove_edit_note_widget = attrsetter(self, "editor_note", None)
                persist_note = schedulable(registry.save_note, note=data_note)
                return sch_cb(persist_note, remove_edit_note_widget, timeout=0.1)
            case AddNoteEvent():
                data_note = registry.new_note(category=self.note_category, idx=None)
                add_edit_note_widget = attrsetter(self, "editor_note", data_note)
                trigger_display_add = schedulable(
                    self.display_state_trigger, DisplayState.ADD
                )
                return sch_cb(add_edit_note_widget, trigger_display_add, timeout=0.1)
            case EditNoteEvent(category=category, idx=idx):
                data_note = registry.edit_note(category=category, idx=idx)
                add_edit_note_widget = attrsetter(self, "editor_note", data_note)
                trigger_display_edit = schedulable(
                    self.display_state_trigger, DisplayState.EDIT
                )
                return sch_cb(add_edit_note_widget, trigger_display_edit, timeout=0.1)
            case CancelEditEvent():
                trigger_display = schedulable(
                    self.display_state_trigger, DisplayState.DISPLAY
                )
                registry_paginate = schedulable(registry.paginate_note, direction=0)
                remove_edit_note = attrsetter(self, "editor_note", None)
                return sch_cb(
                    trigger_display, registry_paginate, remove_edit_note, timeout=0.1
                )
            case PaginationEvent(direction=direction):
                registry_paginate = schedulable(
                    registry.paginate_note, direction=direction
                )
                return Clock.schedule_once(registry_paginate)
            case FilePickerEvent() as pick_event:
                return self.registry.handle_picker_event(pick_event)

            case (
                CreateCategoryEvent(
                    action=action, category=category, img_path=img_path
                ) as event
            ):
                event_action = event.Action
                match action, category, img_path:
                    case event_action.OPEN_FORM, _, _:
                        return self.display_state_trigger(DisplayState.CATEGORY_EDITOR)
                    case event_action.CLOSE_FORM | event_action.CLOSE_REJECT, _, _:
                        return self.display_state_trigger(self.display_state_last)
                    case event_action.CLOSE_ACCEPT, str(category), img_path:
                        Logger.info(
                            f"{type(self).__name__}: process_event - Create Category {category}"
                        )

                        # Scheduled callback will switch display state to display_state last trigger
                        # as well as push a refresh event to the registry
                        @schedulable
                        def on_category_created():
                            self.display_state_trigger("choose")
                            self.registry.query_all(on_complete=None)

                        self.registry.create_category(
                            category, img_path, on_complete=on_category_created
                        )
                        return self.display_state_trigger(self.display_state_last)

            case _:
                Logger.info(
                    f"{type(self).__name__}: process_event - Unhandled Event {type(event).__name__}"
                )
                return None

    def key_input(self, _window, key, _scancode, _codepoint, _modifier):
        if key == 27:  # Esc Key
            # Back Button Event
            self.registry.push_event(BackButtonEvent(display_state=self.display_state))
            return True
        return False

    """Kivy"""

    def build(self):
        truthy = {True, "1", "True"}
        # noinspection PyUnresolvedReferences
        self.register_event_type("on_paginate")
        self.platform_android = platform == "android"
        self.registry.app = self
        self.display_state_trigger = trigger_factory(
            self, "display_state", self.__class__.display_state_current.options
        )
        Window.bind(on_keyboard=self.key_input)
        storage_path = (
            np if (np := self.config.get("Storage", "NOTES_PATH")) != "None" else None
        )

        if storage_path:
            self.registry.set_note_storage_path(storage_path)
        self.note_service.note_sorting = self.config.get("Behavior", "NOTE_SORTING")
        self.note_service.note_sorting_ascending = (
            self.config.get("Behavior", "NOTE_SORTING_ASCENDING") in truthy
        )
        self.note_service.category_sorting = self.config.get(
            "Behavior", "CATEGORY_SORTING"
        )
        self.note_service.category_sorting_ascending = (
            self.config.get("Behavior", "CATEGORY_SORTING_ASCENDING") in truthy
        )
        sm = NoteAppScreenManager()
        self.screen_manager = sm

        # Invokes note_service.discover_notes
        self.registry.query_all()

        self.base_font_size = self.config.get("Display", "BASE_FONT_SIZE")
        Clock.schedule_interval(self.process_event, 1e-4)
        self.plugin_manager.init_app(self)
        sm.fbind(
            "on_interact", lambda _: self.plugin_manager.plugin_event("on_interact")
        )

        return sm

    def build_settings(self, settings: Settings):
        settings.add_json_panel("MindRef", self.config, data=json.dumps(app_settings))

    def build_config(self, config: Config):
        config.setdefaults(
            "Behavior",
            {
                "NOTE_SORTING": "Creation Date",
                "NOTE_SORTING_ASCENDING": False,
                "CATEGORY_SORTING": "Creation Date",
                "CATEGORY_SORTING_ASCENDING": False,
            },
        )

        match platform:  # We can't use self.platform_android yet
            case "android":
                config.setdefaults("Storage", {"NOTES_PATH": None})
                config.setdefaults("Display", {"BASE_FONT_SIZE": 18})
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
                    "Plugins", {"SCREEN_SAVER_ENABLE": False, "SCREEN_SAVER_DELAY": 60}
                )

    def on_config_change(self, config: Config, section: str, key: str, value: Any):
        truthy = {True, "1", "True"}
        Logger.info(f"{type(self).__name__}: on_config_change - {section},{key}")
        match section, key:
            case "Storage", "NOTES_PATH" if not self.platform_android:
                self.note_service.storage_path = value
                self.display_state_trigger(DisplayState.CHOOSE)
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Storage", "NOTES_PATH" if self.platform_android:
                self.registry.set_note_storage_path(value)
                self.display_state_trigger(DisplayState.CHOOSE)
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "NOTE_SORTING":
                self.note_service.note_sorting = value
                self.display_state_trigger(DisplayState.CHOOSE)
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "NOTE_SORTING_ASCENDING":
                self.note_service.note_sorting_ascending = (
                    value if value in truthy else False
                )
                self.display_state_trigger(DisplayState.CHOOSE)
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "CATEGORY_SORTING":
                self.note_service.category_sorting = value
                self.display_state_trigger(DisplayState.CHOOSE)
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "CATEGORY_SORTING_ASCENDING":
                self.note_service.category_sorting_ascending = (
                    value if value in truthy else False
                )
                self.display_state_trigger(DisplayState.CHOOSE)
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Display", "BASE_FONT_SIZE":
                self.base_font_size = int(value)
            case "Plugins", _:
                ...

    def on_pause(self):
        return True
