from pathlib import Path

from dotenv import load_dotenv
from kivy import Logger, platform
from kivy.config import Config
from kivy.core.text import LabelBase


def run_android():
    import shutil

    def bootstrap_c_build():
        # Copy the mindref compiled .so file(s) from the python-for-android build which will be located in the site-packages directory
        # This is architecture dependent but at runtime, the architecture specific site-packages directory will be used automatically
        site_packages = Path(__file__).parent / "_python_bundle" / "site-packages"

        app_lib = Path(__file__).parent / "lib"
        app_lib_ext = app_lib / "ext"

        lib_ext = "ext.so"
        lib_ext_src = site_packages / "mindref_ext" / lib_ext
        lib_ext_dest = app_lib_ext / lib_ext

        def copy_lib(src, dest):
            if not dest.exists():
                Logger.info(f"Copying {src} to {dest}")
                shutil.copy(src, dest)
            else:
                Logger.info(f"{dest} exists")

        # copy_lib(lib_ext_src, lib_ext_dest)

    # bootstrap_c_build()

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
