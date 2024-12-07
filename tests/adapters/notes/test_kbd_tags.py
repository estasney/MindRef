import pytest

from mindref.lib.domain.markdown_note import MarkdownNote


@pytest.fixture
def md_kbd_generator(request, markdown_generator):
    gen = markdown_generator()
    param = request.param
    if param == "kbd":
        return f"{next(gen)}\n<kbd>A</kbd>\n{next(gen)}", True
    if param == "partial":
        return f"{next(gen)}\n<kbd>A\n{next(gen)}", False
    return next(gen), False


def flatten_doc(doc: list[dict]):
    def drill_down(d):
        children = [d]
        if d.get("children"):
            for child in d["children"]:
                children.append(drill_down(child))
        return children

    tags = [drill_down(d) for d in doc]
    tags = [item for sublist in tags for item in sublist]
    tags = [item[0] if isinstance(item, list) else item for item in tags]
    return tags


@pytest.mark.parametrize("md_kbd_generator", ["kbd", "partial", None], indirect=True)
def test_kbd_parsing(md_kbd_generator):
    """
    Given a Markdown formatted file. Check that the <kbd> tag is detected.

    As-is kbd could be detected as codespan
    """
    given, expected = md_kbd_generator
    from io import StringIO

    buf = StringIO()
    buf.write(given)
    buf.seek(0)
    md_file = MarkdownNote.from_buffer(
        category="test", buffer=buf, title="test", idx=1, filepath=None
    )
    doc = md_file.document
    pieces = list(flatten_doc(doc))
    tags = [md.get("type") for md in pieces]
    if expected:
        assert any(t == "kbd" for t in tags), f"NOT DETECTED: {tags}, {md_file.text}"
    else:
        assert not any(t == "kbd" for t in tags), f"DETECTED: {tags}, {md_file.text}"
