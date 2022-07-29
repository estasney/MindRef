import pytest
from PIL import Image, ImageDraw


@pytest.fixture()
def img_maker():
    def _img_maker(width, height):
        img = Image.new(mode="RGB", size=(width, height))
        draw = ImageDraw.Draw(img)
        draw.line((0, 0, *img.size), fill=128, width=10)
        return img

    return _img_maker
