from __future__ import annotations

import pytest

from services.domain import MarkdownNote


@pytest.fixture
def md_files(request, get_expected):
    fp = request.param
    return get_expected(fp)


def test_markdown_note(md_files):
    md_file_doc, conditions = md_files
    doc = MarkdownNote(category="test", idx=0, file=md_file_doc)
    for cond in conditions:
        cond(doc)
