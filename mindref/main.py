from pathlib import Path

from dotenv import load_dotenv
from kivy import Logger
from kivy import platform
from kivy.config import Config
from kivy.core.text import LabelBase


def run_android():
    import shutil

    def util_libs_exist():
        utils_pkg_path = Path(__file__).parent / "_python_bundle" / "site-packages"
        lib_calc = Path(__file__).parent / "utils" / "calculation.so"
        lib_scrolling = Path(__file__).parent / "widgets" / "effects" / "scrolling_c.so"
        if not lib_calc.exists():
            Logger.info("Copying calculation.so")
            shutil.copy(utils_pkg_path / "calculation.so", lib_calc)
        else:
            Logger.info("calculation.so exists")
        lib_index = Path(__file__).parent / "utils" / "index.so"
        if not lib_index.exists():
            Logger.info("Copying index.so")
            shutil.copy(utils_pkg_path / "index.so", lib_index)
        else:
            Logger.info("index.so exists")
        if not lib_scrolling.exists():
            Logger.info("Copying scrolling_c.so")
            shutil.copy(utils_pkg_path / "scrolling_c.so", lib_scrolling)
        else:
            Logger.info("scrolling_c.so exists")

    Logger.info("Copying Lib Files")
    util_libs_exist()

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
