import mistune
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .md_parser_types import MD_DOCUMENT


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls.__instance
        else:
            return cls.__instance


class MarkdownParser(metaclass=Singleton):
    _parser: mistune.Markdown

    def __init__(self):
        self._parser = mistune.create_markdown(
            renderer=mistune.AstRenderer(), plugins=["table"]
        )

    def parse(self, text: str) -> "MD_DOCUMENT":
        result = self._parser(text)
        return result
