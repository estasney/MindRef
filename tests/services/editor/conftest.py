from pathlib import Path

import pytest

from services.domain import MarkdownNote


@pytest.fixture()
def md_note(tmpdir):
    """Write a simple MD Note to file"""
    fp = Path(tmpdir) / "testnote.md"
    doc = """
    # Test Note
    
    Testing, testing ... 123
    """
    fp.write_text(doc, encoding="utf-8")
    md = MarkdownNote(category="test", idx=0, file=fp)
    yield md
    fp.unlink()
