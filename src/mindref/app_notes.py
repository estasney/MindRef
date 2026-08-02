from dataclasses import dataclass
from pathlib import Path


@dataclass
class NoteFile:
    file_path: Path
    label: str
    id: str

    def __post_init__(self):
        self.file_path = Path(self.file_path)
        self.label = self.file_path.stem.replace("_", " ").strip()
        self.id = str(self.file_path)

    @classmethod
    def from_path(cls, path: str | Path) -> "NoteFile":
        path = Path(path)
        return cls(file_path=path, label=path.stem, id=str(path))

    def read_text(self, encoding: str = "utf-8") -> str:
        """Read the content of the note file."""
        return self.file_path.read_text(encoding=encoding)
