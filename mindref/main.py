import sys
from pathlib import Path
from dotenv import load_dotenv
from kivy import Logger
from kivy import platform
from kivy.config import Config
from kivy.core.text import LabelBase


def run_android():
    import shutil

    def bootstrap_c_build():
        # Copy the .so files from the python-for-android build which will be located in the site-packages directory
        cython_build_path = Path(__file__).parent / "_python_bundle" / "site-packages"

        app_lib = Path(__file__).parent / "lib"
        app_utils = app_lib / "utils"
        app_widgets = app_lib / "widgets"

        lib_calc = "calculation.so"
        lib_index = "index.so"
        lib_scrolling = "scrolling_c.so"

        lib_calc_src = cython_build_path / lib_calc
        lib_index_src = cython_build_path / lib_index
        lib_scrolling_src = cython_build_path / lib_scrolling

        lib_calc_dest = app_utils / lib_calc
        lib_index_dest = app_utils / lib_index
        lib_scrolling_dest = app_widgets / "effects" / lib_scrolling

        if not lib_calc_dest.exists():
            Logger.info(f"Copying {lib_calc_src} to {lib_calc_dest}")
            shutil.copy(lib_calc_src, lib_calc_dest)
        else:
            Logger.info("calculation.so exists")

        if not lib_index_dest.exists():
            Logger.info(f"Copying {lib_index_src} to {lib_index_dest}")
            shutil.copy(lib_index_src, lib_index_dest)
        else:
            Logger.info("index.so exists")

        if not lib_scrolling_dest.exists():
            Logger.info(f"Copying {lib_scrolling_src} to {lib_scrolling_dest}")
            shutil.copy(lib_scrolling_src, lib_scrolling_dest)
        else:
            Logger.info("scrolling_c.so exists")

    bootstrap_c_build()

    Logger.info("Running Android")

    from app import MindRefApp

    app = MindRefApp()
    app.run()


def run_desktop():
    import os

    load_dotenv()
    if os.environ.get("ENVIRONMENT", "PRODUCTION") == "DEBUG":
        Config.set("modules", "inspector", "")
        # Config.set("modules", "monitor", "")
        # Config.set("modules", "webdebugger", "")
    else:
        Config.remove_option("modules", "monitor")
        Config.remove_option("modules", "inspector")

    Config.set("input", "mouse", "mouse,disable_multitouch")

    from app import MindRefApp

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

    # Ensure that the current directory is in the path
    package_path = Path(__file__).parent
    if str(package_path) not in sys.path:
        sys.path.append(str(package_path))

    match platform:
        case "android":
            run_android()
        case _:
            run_desktop()


if __name__ == "__main__":
    main()
