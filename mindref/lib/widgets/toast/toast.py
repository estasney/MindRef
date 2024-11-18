import weakref
from typing import Optional, Callable

from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.popup import Popup

from lib.utils import import_kv

import_kv(__file__)


class Toast(Popup):
    id: StringProperty("")
    title = StringProperty("")
    text = StringProperty("")
    content = ObjectProperty()
    duration = NumericProperty(5)

    def __init__(
        self, on_close: Optional[Callable[[str], None]], duration: int, **kwargs
    ):
        self.handle_on_close = weakref.ref(on_close) if on_close is not None else None
        self.duration = duration
        super().__init__(**kwargs)

    def on_open(self):
        Clock.schedule_once(self.dismiss, self.duration)

    def on_dismiss(self):
        if self.handle_on_close is not None:
            on_close = self.handle_on_close()
            if on_close is not None:
                on_close(self.id)

    @classmethod
    def show_toast(
        cls,
        title: str,
        text: str,
        on_close: Optional[Callable[[str], None]],
        duration: int = 5,
    ):
        toast = cls(title=title, text=text, duration=duration, on_close=on_close)
        toast.open()
