from pathlib import Path

from dotenv import load_dotenv
from kivy import Logger
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy import platform


def run_android():
    Logger.info("Running Android")
    from mindref import MindRefApp

    app = MindRefApp()
    app.run()


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

    match platform:
        case "android":
            run_android()
        case _:
            run_desktop()
