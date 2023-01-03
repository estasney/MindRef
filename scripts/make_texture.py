from collections import namedtuple
from math import sqrt
from pathlib import Path

from PIL import Image, ImageDraw
from colour import Color

c1 = Color("#6d7272")
c2 = Color("#388fe5")

TextureParam = namedtuple(
    "TextureParam", "main, accent, steps, step_size, size, opacity_padding, radius"
)
ImgBox = namedtuple("ImgBox", "x,y,w,h")


def point_distance(xy1, xy2):
    dx = xy1[0] - xy2[0]
    dy = xy1[1] - xy2[1]

    return sqrt(dx**2 + dy**2)


def gradient_texture(
    main: Color,
    accent: Color,
    steps: int,
    step_size,
    size,
    opacity_padding: int = 2,
    radius=16,
):
    """
    Generate 9-scaling texture image

    Parameters
    ----------
    main:
        Main color
    accent:
        Accent color
    steps:
        Number of steps from accent to main
    step_size
        Pixel size of step
    radius
        for rounded rectangle
    size: int
        (width/height) of image. Assumed to be square
    opacity_padding
        Number of pixels to surround solid color with 50% opacity
    """

    # Solid colors

    c_steps = list(accent.range_to(main, steps))
    img = Image.new(mode="RGBA", size=(size, size))
    draw = ImageDraw.Draw(img)

    px0 = opacity_padding
    px1 = size - opacity_padding - step_size

    draw.rectangle((0, 0, size, size), fill=f"#00000000")

    for c in c_steps:
        draw.rounded_rectangle((px0, px0, px1, px1), fill=f"{c.hex_l}ff", radius=radius)
        px0 += step_size
        px1 -= step_size

    return img


if __name__ == "__main__":
    btn_down = TextureParam(
        main=Color("#ffffff"),
        accent=Color("#343a40"),
        steps=5,
        size=64 * 4,
        step_size=1,
        radius=4,
        opacity_padding=2,
    )
    btn_down_nb = TextureParam(
        main=Color("#ffffff"),
        accent=Color("#ffffff"),
        steps=5,
        size=64 * 4,
        step_size=1,
        radius=0,
        opacity_padding=0,
    )
    btn_normal = TextureParam(
        main=Color("#ffffff"),
        accent=Color("#000000"),
        steps=5,
        size=64 * 4,
        step_size=1,
        radius=4,
        opacity_padding=4,
    )
    btn_normal_nb = TextureParam(
        main=Color("#ffffff"),
        accent=Color("#ffffff"),
        steps=5,
        size=64 * 4,
        step_size=1,
        radius=0,
        opacity_padding=0,
    )
    btn_disabled = TextureParam(
        main=Color("#8f8f8f"),
        accent=Color("#000000"),
        steps=5,
        size=64 * 4,
        step_size=1,
        radius=4,
        opacity_padding=4,
    )
    btn_disabled_nb = TextureParam(
        main=Color("#8f8f8f"),
        accent=Color("#8f8f8f"),
        steps=5,
        size=64 * 4,
        step_size=1,
        radius=0,
        opacity_padding=0,
    )

    texture_path = Path(__file__).parent.parent / "mindref" / "static" / "textures"
    for file in texture_path.iterdir():
        file.unlink()

    gradient_texture(**btn_down._asdict()).save(texture_path / "bg_down.png")
    gradient_texture(**btn_down_nb._asdict()).save(texture_path / "bg_down_nb.png")
    gradient_texture(**btn_normal._asdict()).save(texture_path / "bg_normal.png")
    gradient_texture(**btn_normal_nb._asdict()).save(texture_path / "bg_normal_nb.png")
    gradient_texture(**btn_disabled._asdict()).save(texture_path / "bg_disabled.png")
    gradient_texture(**btn_disabled_nb._asdict()).save(
        texture_path / "bg_disabled_nb.png"
    )
