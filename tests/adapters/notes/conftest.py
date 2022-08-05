import random
from string import printable

import pytest


@pytest.fixture()
def markdown_generator():
    """Spit out valid markdown"""

    def _markdown_generator():
        def random_line():
            return "".join(random.choices(printable, k=random.randint(1, 255)))

        while True:
            strategy = random.choice(("text", "code", "heading"))
            if strategy == "heading":
                yield ("#" * random.randint(1, 4)) + random_line()
                continue
            if strategy == "code":
                chunk = ["```python", random_line()]
                while random.randint(0, 1) < 1:
                    chunk.append(random_line())
                chunk.append("```")
                yield "\n".join(chunk)
                continue
            if strategy == "text":
                yield "\n".join((random_line() for i in range(random.randint(1, 5))))
                continue

    return _markdown_generator
