from PIL import Image, ImageDraw
from colour import Color

c1 = Color("#6d7272")
c2 = Color("#388fe5")


def gradient_texture(tx_size, color_main: Color, color_accent: Color, n_steps: int):
    """
    Generate 9-scaling texture image

    Parameters
    ----------
    tx_size: int
        (width/height) of image. Assumed to be square
    color_main:
    color_accent:
    n_steps:
    """
    c_steps = list(color_accent.range_to(color_main, n_steps))
    img = Image.new(mode="RGB", size=(tx_size, tx_size))
    draw = ImageDraw.Draw(img)

    px0 = 0
    px1 = tx_size - 1

    for c in c_steps:
        draw.rectangle((px0, px0, px1, px1), fill=c.hex_l)
        px0 += 1
        px1 -= 1

    return img


if __name__ == "__main__":
    btn_press = [Color("#4a99e8"), Color("#388fe5")]
    btn_normal = [Color("#37464f"), Color("#101f27")]

    gradient_texture(64, *btn_press, n_steps=5).save(
        "../kvnoteafly/static/textures/bg_down.png"
    )
    gradient_texture(64, *btn_normal, n_steps=5).save(
        "../kvnoteafly/static/textures/bg_normal.png"
    )
