from pathlib import Path

from dotenv import load_dotenv
from kivy import Logger, platform
from kivy.config import Config
from kivy.core.text import LabelBase


def run_android():
    Logger.info("Running Android")
    from mindref.app import MindRefApp

    app = MindRefApp()
    app.run()


def run_desktop():
    import os

    load_dotenv()
    if os.environ.get("ENVIRONMENT", "PRODUCTION") == "DEBUG":
        Config.set("modules", "inspector", "")
    else:
        Config.remove_option("modules", "monitor")
        Config.remove_option("modules", "inspector")

    Config.set("input", "mouse", "mouse,disable_multitouch")

    from mindref.app import MindRefApp

    app = MindRefApp()

    app.run()


def main():
    LabelBase.register(
        name="RobotoMono",
        fn_regular=str(Path(__file__).parent / "assets" / "RobotoMono-Regular.ttf"),
    )
    LabelBase.register(
        name="Icon",
        fn_regular=str(Path(__file__).parent / "assets" / "MaterialIcons.ttf"),
    )

    match platform:
        case "android":
            run_android()
        case _:
            run_desktop()


if __name__ == "__main__":
    main()
