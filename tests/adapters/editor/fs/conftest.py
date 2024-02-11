from pathlib import Path

import pytest

from lib.domain.markdown_note import MarkdownNote


@pytest.fixture()
def md_note(tmpdir):
    """Write a simple MD Note to file"""
    fp = Path(tmpdir) / "testnote.md"
    doc = """
    # Test Note
    
    Testing, testing ... 123
    """
    fp.write_text(doc, encoding="utf-8")
    md = MarkdownNote.from_file(category="test", idx=0, fp=fp)
    yield md
    fp.unlink()
