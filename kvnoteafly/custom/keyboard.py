from functools import partial

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from utils import import_kv

import_kv(__file__)


class KeyboardLabelSeparatorOuter(Widget):
    background_color = get_color_from_hex("#0e0e0e")


class KeyboardLabelSeparatorInner(Label):
    background_color = get_color_from_hex("#0e0e0e")
    FONT_COLOR = "#eeeeee"
    FONT_SIZE = 36

    def __init__(self, **kwargs):
        markup_text = f"[color={self.FONT_COLOR}] + [/color]"
        super().__init__(
            text=markup_text, markup=True, font_size=self.FONT_SIZE, **kwargs
        )


class KeyboardImage(Image):
    pressed = BooleanProperty(False)

    def __init__(self, **kwargs):
        text = kwargs.pop("text")
        # src = os.path.join("static", "keys", text.lower()) + ".png"
        src = f"atlas://static/keys/keys/{text.lower()}"
        super().__init__(source=src, **kwargs)

    def on_pressed(self, obj, value):
        if value:
            animation_press = Animation(y=self.y - 7, duration=0.15, t="out_cubic")
        else:
            animation_press = Animation(y=self.y + 7, duration=0.15, t="out_cubic")
        animation_press.start(self)


class KeyboardLabel(Label):
    background_color = get_color_from_hex("#eeeeee")
    FONT_COLOR = "#0e0e0e"
    FONT_SIZE = 36

    def __init__(self, **kwargs):
        markup_text = f"[color={self.FONT_COLOR}]{kwargs.pop('text')}[/color]"
        super(KeyboardLabel, self).__init__(
            text=markup_text, markup=True, font_size=self.FONT_SIZE, **kwargs
        )


class ContentKeyboard(BoxLayout):
    note_text = StringProperty()
    keyboard_buttons = ListProperty()
    keyboard_animated_widgets = ListProperty()
    key_container = ObjectProperty()

    HSPACE_MULTI = 0.5
    HSPACE_MULTI_INNER_SEP = 0.2
    HSPACE_SINGLE = 0.2
    ANIMATION_WINDOW = 2

    def __init__(self, content_data, **kwargs):
        self.note_text = content_data["text"] if content_data["text"] else ""
        self.keyboard_buttons = content_data["keys_str"].split(",")
        super(ContentKeyboard, self).__init__(**kwargs)
        self.on_keyboard_buttons()

    @staticmethod
    def _set_btn_pressed(*args):
        btn, value, *_ = args
        try:
            btn.pressed = value
        except ReferenceError:
            pass

    @staticmethod
    def _unset_btns_pressed(*args):
        btns, *_ = args
        for btn in btns:
            try:
                ContentKeyboard._set_btn_pressed(btn, False)
            except ReferenceError:
                pass

    def _schedule_animations(self, *args, **kwargs):
        animation_interval = self.ANIMATION_WINDOW / len(self.keyboard_animated_widgets)

        for i, btn in enumerate(self.keyboard_animated_widgets, start=1):
            func = partial(self._set_btn_pressed, btn, True)
            Clock.schedule_once(func, (animation_interval * i))

        Clock.schedule_once(
            partial(self._unset_btns_pressed, self.keyboard_animated_widgets),
            self.ANIMATION_WINDOW + 1,
        )

    def on_keyboard_buttons(self, *args, **kwargs):
        self.key_container.clear_widgets()
        n_btns = len(self.keyboard_buttons)
        last_btn = n_btns - 1

        # Multiple Keyboard buttons should take up 50% of horizontal Space
        # Inner spacers take 20% of 50%
        # Single buttons should take up 50% of horizontal space
        # Inner spacing is n_buttons - 1

        if n_btns == 1:
            outer_sep_size = (1 - self.HSPACE_SINGLE) / 2

            self.key_container.add_widget(
                KeyboardLabelSeparatorOuter(size_hint=(outer_sep_size, 1))
            )
            kb_img = KeyboardImage(
                text=self.keyboard_buttons[0], size_hint=(self.HSPACE_SINGLE, 1)
            )
            self.keyboard_animated_widgets.append(kb_img.proxy_ref)
            self.key_container.add_widget(kb_img)
            self.key_container.add_widget(
                KeyboardLabelSeparatorOuter(size_hint=(outer_sep_size, 1))
            )
        else:
            outer_sep_size = (1 - self.HSPACE_MULTI) / 2
            inner_size = 1 - self.HSPACE_MULTI
            inner_sep_size = (inner_size * self.HSPACE_MULTI_INNER_SEP) / (n_btns - 1)
            inner_size_img = (inner_size - inner_sep_size) / n_btns

            for i, btn in enumerate(self.keyboard_buttons):
                if i == 0:
                    self.key_container.add_widget(
                        KeyboardLabelSeparatorOuter(size_hint=(outer_sep_size, 1))
                    )
                if n_btns >= i > 0:
                    self.key_container.add_widget(
                        KeyboardLabelSeparatorInner(size_hint=(inner_sep_size, 1))
                    )
                kb_img = KeyboardImage(text=btn, size_hint=(inner_size_img, 1))
                self.keyboard_animated_widgets.append(kb_img.proxy_ref)
                self.key_container.add_widget(kb_img)
                if i == last_btn:
                    self.key_container.add_widget(
                        KeyboardLabelSeparatorOuter(size_hint=(outer_sep_size, 1))
                    )

        Clock.schedule_once(self._schedule_animations, 0)
