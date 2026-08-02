from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from kivy.uix.effectwidget import EffectWidget

from mindref.lib.widgets.effects.linear_progress import LinearProgressEffect

Builder.load_string("""
#:import LinearProgressEffect mindref.lib.widgets.effects.linear_progress.LinearProgressEffect
<LinearProgress>:
    BoxLayout:
        layout: 'horizontal'
        size_hint_y: None
        height: root.height
        
""")


class LinearProgress(EffectWidget):
    grad_start = ListProperty([0.06, 0.50, 0.98])
    grad_end = ListProperty([0.38, 0.80, 1.00])
    speed = NumericProperty(3.0)
    bar_width = NumericProperty(3.0)
    animated = BooleanProperty(False)
    effects = ListProperty()

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        fbind = self.fbind
        fbind("grad_start", self.setup_effect)
        fbind("grad_end", self.setup_effect)
        fbind("speed", self.setup_effect)
        fbind("bar_width", self.setup_effect)
        fbind("animated", self.toggle_effect)

    def setup_effect(self):
        """
        Initialize the linear progress effect.
        """
        self.effects = [
            LinearProgressEffect(
                grad_start=self.grad_start,
                grad_end=self.grad_end,
                speed=self.speed,
                bar_width=self.bar_width,
            )
        ]

    def toggle_effect(self, *_args: object) -> None:
        """
        Enable or disable the linear progress effect based on the animated property.
        """
        Logger.info(
            f"LinearProgress: {'Enabling' if self.animated else 'Disabling'} effect"
        )
        if self.animated:
            self.setup_effect()
        else:
            self.effects = []
