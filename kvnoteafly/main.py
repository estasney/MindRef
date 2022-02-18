from noteafly import NoteAFly
import os
import requests


def handle_android():
    url = "https://raw.githubusercontent.com/estasney/KVNoteAFly/master/db/noteafly.db"
    r = requests.get(url)
    with open("./db/noteafly.db", "wb") as fp:
        fp.write(r.content)
    print("Updated DB")


if __name__ == '__main__':
    if os.environ.get('ANDROID_ENTRYPOINT', None):
        handle_android()
    NoteAFly().run()
