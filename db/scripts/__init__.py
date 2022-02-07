import os
from typing import Set

import click
import pygments.lexers
import pyperclip
from subprocess import Popen, PIPE

from pygments.util import ClassNotFound

from kvnoteafly.db.models import create_session, Note, NoteCategory, NoteType

LAST_CATEGORY = None
LAST_NOTE_TYPE = None
LAST_LEXER = None
KEYCHARS = None


@click.command()
def create():
    """Simple script to quickly create notes"""
    click.echo("This is a simple program to create notes via clipboard")
    session = create_session()
    while True:
        try:
            make_new = input("Create a new note? [y/n]")
            if make_new == "y":
                create_note(session)
            else:
                commit_changes = input("Commit Notes and Push? [y/n]")
                if commit_changes == "n":
                    click.echo("Notes saved but not committed")
                    click.echo("Goodbye")
                    return
                else:
                    commit_notes()
                    click.echo("Notes saved and committed")
                    click.echo("Goodbye")
                    return
        except Exception as e:
            print(e)
            click.echo("Exception Occurred")
            click.echo("Goodbye")
            return

def commit_notes():
    db_path = "../noteafly.db"

    with Popen(['git', 'add', db_path], stdout=PIPE, stderr=PIPE) as p:
        result, _ = p.communicate()
        result = result.decode().strip()
        print(result)

    with Popen(['git', 'commit', '-m', 'add note'], stdout=PIPE, stderr=PIPE) as p:
        result, _ = p.communicate()
        result = result.decode().strip()
        print(result)

    with Popen(['git', 'push'], stdout=PIPE, stderr=PIPE) as p:
        result, _ = p.communicate()
        result = result.decode().strip()
        print(result)






def get_available_keys() -> Set[str]:
    from kvnoteafly import __file__ as package_file
    import json
    package_dir = os.path.dirname(package_file)
    key_atlas_fp = os.path.join(package_dir, "static", "keys", "keys.atlas")
    with open(key_atlas_fp, "r") as kp:
        key_atlas = json.load(kp)
    key_chars = set([])
    for filename, keys_data in key_atlas.items():
        key_chars.update(set(keys_data.keys()))

    return key_chars


def get_params():
    global LAST_CATEGORY, LAST_NOTE_TYPE
    if all([LAST_CATEGORY, LAST_NOTE_TYPE]):
        print(f"Last used\nCategory: {LAST_CATEGORY}\nNote_Type: {LAST_NOTE_TYPE}")
        use_same = input("Use the same params? [y/n]")
        if use_same == "y":
            return {"category": LAST_CATEGORY, "note_type": LAST_NOTE_TYPE}
    # category
    categories = {i: NoteCategory(i) for i in range(len(NoteCategory))}
    for k, v in categories.items():
        print(f"{k} : {v.name}")

    user_cat = int(input(f"Select category [{min(categories)}-{max(categories)}]: "))

    # note type
    note_types = {i: NoteType(i) for i in range(len(NoteType))}
    for k, v in note_types.items():
        print(f"{k} : {v.name}")

    user_type = int(input(f"Select note type [{min(note_types)}-{max(note_types)}]: "))

    LAST_CATEGORY = user_cat
    LAST_NOTE_TYPE = user_type
    return {"category": LAST_CATEGORY, "note_type": LAST_NOTE_TYPE}


def create_note(session):
    global KEYCHARS
    params = get_params()
    note_type = params['note_type']
    note_category = params['category']



    def validate_key(char) -> bool:
        global KEYCHARS
        if KEYCHARS is None:
            KEYCHARS = get_available_keys()
        return char.lower() in KEYCHARS


    def handle_key_note():
        keys = []
        while True:
            try:
                if keys:
                    print(",".join(keys))
                key = input("Enter a key, type 'done' when finished : ")
                if key == 'done':
                    note = Note()
                    note.keys = keys
                    note.category = NoteCategory(note_category)
                    note.note_type = NoteType(note_type)
                    note.code_lexer = None
                    return note
                else:
                    key_valid = validate_key(key)
                    if key_valid:
                        keys.append(key)
                    else:
                        print(f"No Key image found for {key.lower()}")
                        print("""Choose an option:
                        y : Accept
                        n : Discard (default)
                        ? : Discard and show available keys
                        """)
                        decision = input(f"Enter option : ")
                        if decision == "y":
                            keys.append(key)
                            continue
                        if decision == "?":
                            print(", ".join(sorted(list(KEYCHARS))))
                            continue
                        else:
                            continue
            except:
                return None

    def handle_code_note():
        global LAST_LEXER
        code_lexer = None
        while True:
            cl = input(f"Lexer ? [{LAST_LEXER if LAST_LEXER else 'Python'}]")
            if not cl:
                cl = LAST_LEXER if LAST_LEXER else 'Python'
            try:
                pygments.lexers.get_lexer_by_name(cl)
                LAST_LEXER = cl
                code_lexer = cl
                break
            except ClassNotFound:
                print(f"{cl} is not a valid lexer")
                continue

        ok = input("Ready to get clipboard contents? [y/n]")
        if ok == "n":
            return

        note = Note()
        note.text = pyperclip.paste()
        note.category = NoteCategory(params['category'])
        note.note_type = NoteType(params['note_type'])
        note.code_lexer = code_lexer
        return note

    def handle_other_note():
        ok = input("Ready to get clipboard contents? [y/n]")
        if ok == "n":
            return

        note = Note()
        note.text = pyperclip.paste()
        note.category = NoteCategory(params['category'])
        note.note_type = NoteType(params['note_type'])
        return note

    if note_type == NoteType.KEYBOARD_NOTE.value:
        note = handle_key_note()
    elif note_type == NoteType.CODE_NOTE.value:
        note = handle_code_note()
    else:
        note = handle_other_note()
    if note:
        note.title = input("Note Title ?")
        session.add(note)
        session.commit()


if __name__ == '__main__':
    create()
