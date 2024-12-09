from __future__ import annotations

import asyncio
from collections.abc import Sequence
from pathlib import Path

from PIL import Image


async def _read_img_size(f: Path | str) -> tuple[int, int]:
    img = Image.open(f)
    return img.width, img.height


async def read_img_sizes(
    imgs: Sequence[Path | str],
) -> dict[Path | str, tuple[int, int]]:
    sizes = await asyncio.gather(*[_read_img_size(f) for f in imgs])
    return {f: size for f, size in zip(imgs, sizes, strict=False)}
