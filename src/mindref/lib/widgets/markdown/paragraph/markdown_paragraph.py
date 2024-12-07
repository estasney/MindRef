from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from pygments import styles

from mindref.lib.utils import import_kv

import_kv(__file__)


class MarkdownParagraph(GridLayout):
    text_content = StringProperty()
    content = ObjectProperty()
    background_color = StringProperty()

    def __init__(self, **kwargs):
        super(MarkdownParagraph, self).__init__(**kwargs)
        self.styler = styles.get_style_by_name("paraiso-dark")
        self.background_color = self.styler.background_color
