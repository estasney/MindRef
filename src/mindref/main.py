from pathlib import Path

from dotenv import load_dotenv
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy.logger import Logger
from kivy.utils import platform

from mindref.app import MindRefApp


def run_android():
    Logger.info("Running Android")
    from mindref.app import MindRefApp

    app = MindRefApp(platform_android=True)
    app.run()


def setup_desktop() -> MindRefApp:
    import os

    load_dotenv()
    if os.environ.get("ENVIRONMENT", "PRODUCTION") == "DEBUG":
        Config.set("modules", "inspector", "")
    else:
        Config.remove_option("modules", "monitor")
        Config.remove_option("modules", "inspector")

    Config.set("input", "mouse", "mouse,disable_multitouch")

    enable_profiling = os.environ.get("PROFILE") is not None

    from mindref.app import MindRefApp

    return MindRefApp(enable_profiling=enable_profiling)


def run_desktop():
    app = setup_desktop()
    app.run()


def main():
    LabelBase.register(
        name="JetBrainsMono",
        fn_regular=str(Path(__file__).parent / "assets" / "JetBrainsMono-Regular.ttf"),
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
