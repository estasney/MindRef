from noteafly import NoteAFly
import os
import requests


def handle_android():
    url = "https://github.com/estasney/KVNoteAFly/blob/master/kvnoteafly/db/noteafly.db?raw=true"
    r = requests.get(url)
    with open("./db/noteafly.db", "wb") as fp:
        fp.write(r.content)
    print("Updated DB")


if __name__ == "__main__":
    if os.environ.get("ANDROID_ENTRYPOINT", None):
        handle_android()
    NoteAFly().run()
