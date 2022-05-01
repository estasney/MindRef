import click
from pathlib import Path
from kvnoteafly.db.models import create_session, Note, NoteCategory, NoteType


@click.command()
@click.argument("store_path", type=click.Path(path_type=Path, dir_okay=True))
@click.argument("db", type=click.Path(path_type=Path, exists=True))
def export_notes_to_files(store_path: Path, db: Path):
    session = create_session(f"sqlite:///{db.as_posix()}")
    categories = [c[0].name for c in session.query(Note.category).distinct().all()]
    store_path.mkdir(exist_ok=True)
    for cat in categories:
        cat_path = store_path / cat
        cat_path.mkdir(exist_ok=True)
        cat_notes = session.query(Note).filter(Note.category == cat).all()
        for note in cat_notes:
            if note.note_type == NoteType.KEYBOARD_NOTE:
                title, text = handle_key_note(note)
            elif note.note_type == NoteType.TEXT_NOTE:
                title, text = handle_text_note(note)
            elif note.note_type == NoteType.CODE_NOTE:
                title, text = handle_code_note(note)
            else:
                ...
            note_path = (cat_path / title).with_suffix(".md")
            with note_path.open(mode="w+", encoding="utf-8") as fp:
                fp.write(f"{text}\n")


def handle_code_note(note):
    text = (
        f"# {note.title}\n"
        f"```{note._code_lexer.lower() if note._code_lexer else 'python'}\n"
        f"{note.text}\n"
        f"```\n"
    )
    return note.title, text


def handle_text_note(note):

    text = f"""
        # {note.title}
        
        {note.text}
    """
    return note.title, text


def handle_key_note(note):
    title_header = note.text if note.text else note.title
    text = f"# {title_header}\n" f"```shortcut\n" f"{note.keys_str}\n" f"```"

    return note.title, text


if __name__ == "__main__":
    export_notes_to_files()
