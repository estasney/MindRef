from dotenv import load_dotenv
from kivy import Logger
from kivy.core.text import LabelBase
from kivy.config import Config
from pathlib import Path
import os


def run_android():
    def start_app(*args):
        os.environ.update({"NOTES_PATH": primary_external_storage_path()})
        from noteafly import NoteAFly

        NoteAFly().run()

    from android.storage import primary_external_storage_path  # noqa
    from android.permissions import request_permissions, Permission, check_permission

    if not check_permission(Permission.READ_EXTERNAL_STORAGE):
        Logger.info(f"Requesting Permissions")
        request_permissions([Permission.READ_EXTERNAL_STORAGE], start_app)
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
    LabelBase.register(
        name="RobotoMono",
        fn_regular=str(Path(__file__).parent / "assets" / "RobotoMono-Regular.ttf"),
    )
    if os.environ.get("ANDROID_ENTRYPOINT", None):
        run_android()
    else:
        run_desktop()
