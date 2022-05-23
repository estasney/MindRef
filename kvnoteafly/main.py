from dotenv import load_dotenv
from kivy.core.text import LabelBase
from kivy.config import Config
from pathlib import Path
import os

load_dotenv()

if __name__ == "__main__":
    LabelBase.register(
        name="RobotoMono",
        fn_regular=str(Path(__file__).parent / "assets" / "RobotoMono-Regular.ttf"),
    )
    if os.environ.get("ANDROID_ENTRYPOINT", None):
        ...
    if os.environ.get("ENVIRONMENT", "PRODUCTION") == "DEBUG":
        Config.set("modules", "inspector", "")
        Config.set("modules", "monitor", "")

    Config.set("input", "mouse", "mouse,disable_multitouch")
    from noteafly import NoteAFly

    NoteAFly().run()
