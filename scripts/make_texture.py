from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw
from colour import Color
from collections import namedtuple

c1 = Color("#6d7272")
c2 = Color("#388fe5")

TextureParam = namedtuple("TextureParam", "main, accent, steps, size")
ImgBox = namedtuple("ImgBox", "x,y,w,h")


def gradient_texture(main: Color, accent: Color, steps: int, size):
    """
    Generate 9-scaling texture image

    Parameters
    ----------
    size: int
        (width/height) of image. Assumed to be square
    main:
    accent:
    steps:
    """
    c_steps = list(accent.range_to(main, steps))
    img = Image.new(mode="RGB", size=(size, size))
    draw = ImageDraw.Draw(img)

    px0 = 0
    px1 = size - 1

    for c in c_steps:
        draw.rectangle((px0, px0, px1, px1), fill=c.hex_l)
        px0 += 1
        px1 -= 1

    return img


if __name__ == "__main__":
    btn_down = TextureParam(
        main=Color("#4a99e8"), accent=Color("#101f27"), steps=15, size=64
    )
    btn_normal = TextureParam(
        main=Color("#37464f"), accent=Color("#101f27"), steps=5, size=64
    )

    texture_path = Path(__file__).parent.parent / "kvnoteafly" / "static" / "textures"
    for file in texture_path.iterdir():
        file.unlink()

    gradient_texture(**btn_down._asdict()).save(texture_path / "bg_down.png")
    gradient_texture(**btn_normal._asdict()).save(texture_path / "bg_normal.png")
