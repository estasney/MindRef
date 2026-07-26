from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

Builder.load_string("""
#:import ExpandingLabel mindref.lib.widgets.style
#:import buttons mindref.lib.widgets.buttons
<Toolbar>:
    orientation: 'horizontal'
    padding: 0
    canvas.before:
        Color:
            rgba: app.colors['Primary']
        Rectangle:
            size: self.size
            pos: self.pos
    OpenMenuButton:
        enable_ripple_effect: False
        on_release: app.menu_open = not app.menu_open
        size_hint: None, None
        width: self.height * sp(1)
        height: self.height
        pos_hint: {'center_y': 0.5}
        padding: 0
        border: 0

    ExpandingLabel:
        text: app.title
        halign: 'center'
        valign: 'center'
        font_size: sp(app.base_font_size)

""")


class Toolbar(BoxLayout): ...
