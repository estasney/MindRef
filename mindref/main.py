from pathlib import Path
from dotenv import load_dotenv
from kivy import Logger
from kivy.core.text import LabelBase
from kivy.config import Config


def run_android():
    def start_app(*args):
        from mindref import MindRefApp
        from android import loadingscreen  # noqa
        from kivy.clock import Clock

        hide_loading = lambda x: loadingscreen.hide_loading_screen()
        Clock.schedule_once(hide_loading)

        # Create default folder
        notes_dir = Path(primary_external_storage_path()) / "mindref_notes"
        notes_dir.mkdir(exist_ok=True)
        os.environ.update({"NOTES_PATH": str(notes_dir)})
        MindRefApp().run()

    # noinspection PyUnresolvedReferences
    from android.storage import primary_external_storage_path

    # noinspection PyUnresolvedReferences
    from android.permissions import (
        request_permissions,
        Permission,
        check_permission,
    )

    if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
        Logger.info(f"Requesting Permissions")
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE], start_app)
    else:
        start_app()


def run_desktop():
    load_dotenv()
    if os.environ.get("ENVIRONMENT", "PRODUCTION") == "DEBUG":
        Config.set("modules", "inspector", "")
        # Config.set("modules", "monitor", "")
        # Config.set("modules", "webdebugger", "")
    else:
        Config.remove_option("modules", "monitor")
        Config.remove_option("modules", "inspector")

    Config.set("input", "mouse", "mouse,disable_multitouch")
    from mindref import MindRefApp

    app = MindRefApp()

    app.run()


if __name__ == "__main__":
    import os

    LabelBase.register(
        name="RobotoMono",
        fn_regular=str(Path(__file__).parent / "assets" / "RobotoMono-Regular.ttf"),
    )

    if os.environ.get("ANDROID_ENTRYPOINT", None):
        run_android()
    else:
        run_desktop()
