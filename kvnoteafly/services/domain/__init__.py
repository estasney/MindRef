from dataclasses import dataclass, asdict, field
from pathlib import Path

from marko.block import Document, Heading


@dataclass
class MarkdownNote:
    text: str
    category: str
    idx: int
    document: Document
    file: Path
    title: str = field(init=False)

    def to_dict(self):
        return asdict(self)

    def __post_init__(self):
        for block in self.document.children:
            if isinstance(block, Heading):
                if block.children and block.children[0].children:
                    self.title = block.children[0].children
                    return
        self.title = self.file.stem.title()
