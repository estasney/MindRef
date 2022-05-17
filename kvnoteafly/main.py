from dotenv import load_dotenv

load_dotenv()
from kivy.config import Config
import os

if __name__ == "__main__":
    if os.environ.get("ANDROID_ENTRYPOINT", None):
        ...
    if os.environ.get("ENVIRONMENT", "PRODUCTION") == "DEVELOPMENT":
        Config.set("modules", "inspector", "")
        Config.set("modules", "monitor", "")

    Config.set("input", "mouse", "mouse,disable_multitouch")
    from noteafly import NoteAFly

    NoteAFly().run()
