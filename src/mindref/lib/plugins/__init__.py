from pathlib import Path
from typing import TYPE_CHECKING, Optional, Protocol, TypeVar

from kivy import Logger
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, NumericProperty, StringProperty

if TYPE_CHECKING:
    from kivy.app import App


class PluginProtocol(Protocol):
    def handle_event(self, event: str): ...

    def is_compatible(self) -> bool: ...


T = TypeVar("T", bound=PluginProtocol)


class PluginManager(EventDispatcher):
    def __init__(self, *args, **kwargs):
        super(PluginManager, self).__init__(*args, **kwargs)
        self.plugins: list[PluginProtocol] = []

    def plugin_event(self, event):
        for plugin in self.plugins:
            plugin.handle_event(event)
        return True

    def init_app(self, app: "App"):
        plugin_config = list(app.config["Plugins"].items())
        # noinspection PyUnresolvedReferences
        app.fbind("on_config_change", self.config_change_handler)
        self.update_plugins(plugin_config)

    def config_change_handler(self, *args):
        value, key, section, *rest = list(reversed(args))

        truthy = {True, "1", "True"}
        falsy = {False, "0", "False"}

        if section != "Plugins":
            return
        if (k := key.lower()).startswith("screen_saver"):
            if k == "screen_saver_enable":
                if value in truthy:
                    ss = self.ensure_plugin(ScreenSaverPlugin, make=True)
                    if not ss:
                        return
                    ss.enabled = ss.is_compatible()
                elif value in falsy:
                    ss = self.ensure_plugin(ScreenSaverPlugin, make=False)
                    if ss:
                        ss.enabled = False
            elif k == "screen_saver_delay":
                ss = self.ensure_plugin(ScreenSaverPlugin, make=False)
                if ss:
                    ss.active_after_minutes = int(value)
        return

    def ensure_plugin(self, plugin_type: type[T], make: bool) -> T | None:
        matched = next((pl for pl in self.plugins if isinstance(pl, plugin_type)), None)
        if matched:
            return matched
        if make:
            pl: T = plugin_type()
            if not pl.is_compatible():
                Logger.info(
                    f"PluginManager: Plugin {pl.__class__.__name__} is not compatible"
                )
                return None
            self.plugins.append(pl)
            return pl
        return None

    def update_plugins(self, config: list[tuple[str, str]]):
        for k, v in config:
            self.config_change_handler(config, "Plugins", k, v)


class ScreenSaverPlugin(EventDispatcher):
    active_after_minutes = NumericProperty(defaultvalue=60)
    elapsed_minutes = NumericProperty(defaultvalue=0)
    enabled = BooleanProperty(defaultvalue=False)
    screen_saved = BooleanProperty(defaultvalue=False)
    sys_fs_path = StringProperty(defaultvalue="/sys/class/backlight", allownone=True)

    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super(ScreenSaverPlugin, self).__init__(*args, **kwargs)
        # Every ~ 60 seconds
        self.trigger = Clock.create_trigger(self.check_time, interval=True, timeout=60)
        self.screen_save_trigger = Clock.create_trigger(self.save_screen)
        self.fbind("enabled", self.handle_enabled)
        self.fbind("screen_saved", self.screen_save_trigger)
        self.sys_fs_path = next(
            map(str, Path(self.sys_fs_path).rglob("*/**/bl_power")), None
        )

    def is_compatible(self) -> bool:
        """If this plugin is enabled, would handle_event raise an Exception"""
        return self.sys_fs_path is not None

    def handle_event(self, event):
        if event == "on_interact":
            self.elapsed_minutes = 0
            Logger.debug(f"ScreenSaverPlugin: elapsed_minutes - {self.elapsed_minutes}")
            self.screen_saved = False

    def handle_enabled(self, *_args):
        if not self.enabled:
            self.trigger.cancel()
        else:
            self.trigger()

    def check_time(self, dt_secs):
        """Check the amount of time elapsed"""
        self.elapsed_minutes = self.elapsed_minutes + (dt_secs / 60)
        if self.active_after_minutes <= self.elapsed_minutes:
            Logger.info("ScreenSaverPlugin: Saving Screen")
            self.screen_saved = True
        else:
            self.screen_saved = False

    def save_screen(self, *_args):
        if not self.sys_fs_path:
            return
        if self.screen_saved:
            # Power off screen
            Path(self.sys_fs_path).write_text("1", encoding="ascii")
        else:
            # Power on screen
            Path(self.sys_fs_path).write_text("0", encoding="ascii")
