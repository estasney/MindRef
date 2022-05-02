from noteafly import NoteAFly
import os


if __name__ == "__main__":
    if os.environ.get("ANDROID_ENTRYPOINT", None):
        ...
    NoteAFly().run()
