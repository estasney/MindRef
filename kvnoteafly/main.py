from pathlib import Path
from dotenv import load_dotenv
from kivy import Logger
from kivy.core.text import LabelBase
from kivy.config import Config


__version__ = "0.0.1"


def run_android():
    def start_app(*args):
        from noteafly import NoteAFly
        from android import loadingscreen  # noqa
        from kivy.clock import Clock

        Clock.schedule_once(loadingscreen.hide_loading_screen)

        # Create default folder
        notes_dir = Path(primary_external_storage_path()) / "kvnotes"
        notes_dir.mkdir(exist_ok=True)
        os.environ.update({"NOTES_PATH": str(notes_dir)})
        NoteAFly().run()

    from android.storage import primary_external_storage_path  # noqa
    from android.permissions import (
        request_permissions,
        Permission,
        check_permission,
    )  # noqa

    if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
        Logger.info(f"Requesting Permissions")
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE], start_app)
    else:
        start_app()


def run_desktop():
    load_dotenv()
    if os.environ.get("ENVIRONMENT", "PRODUCTION") == "DEBUG":
        Config.set("modules", "inspector", "")
        Config.set("modules", "monitor", "")
    Config.set("input", "mouse", "mouse,disable_multitouch")
    from noteafly import NoteAFly

    NoteAFly().run()


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
