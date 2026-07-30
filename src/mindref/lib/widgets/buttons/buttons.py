from kivy.lang import Builder
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    StringProperty,
    VariableListProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from mindref.lib.ext import normalize_coordinates
from mindref.lib.mutation import Mutation
from mindref.lib.utils import mindref_path
from mindref.lib.widgets.effects.ripple import RippleMixin

texture_atlas = "atlas://" + str(mindref_path() / "static" / "textures" / "textures")

Builder.load_string("""
#:import seps mindref.lib.widgets.separator
#:import style mindref.lib.widgets.style
<ThemedButton>:
    background_normal: app.atlas_service.uri_for("bg_normal", atlas_name="textures") if max(self.border) > 0 else app.atlas_service.uri_for("bg_normal_nb", atlas_name="textures")
    background_down: app.atlas_service.uri_for("bg_down", atlas_name="textures") if max(self.border) > 0 else app.atlas_service.uri_for("bg_down_nb", atlas_name="textures")
    background_disabled: app.atlas_service.uri_for("bg_disabled", atlas_name="textures") if max(self.border) > 0 else app.atlas_service.uri_for("bg_disabled_nb", atlas_name="textures")
    state_image: self.background_normal if self.state == 'normal' else self.background_down
    disabled_image: self.background_disabled
    orientation: 'vertical'
    border: dp(8)
    padding: dp(5)
    spacing: dp(2)
    canvas:
        Color:
            rgba: self.background_color
        BorderImage:
            border:  self.border
            pos: self.pos
            size: self.size
            source: self.state_image if not self.disabled else self.disabled_image

<ThemedLabelButton@ThemedButton>:
    text: ''
    size_hint_y: None
    height: self.minimum_height
    canvas:
        Color:
            rgba: self.background_color
        BorderImage:
            border:  self.border
            pos: self.pos
            size: self.size
            source: self.state_image if not root.disabled else self.disabled_image
    BaseLabel:
        text: root.text
        size_hint_y: None
        height: self.texture_size[1] * 2
        color: root.color

<ContainedLabelButton@ThemedLabelButton>:
    disable_ripple_effect: True
    background_color: (0,0,0,0)
    canvas:
        Color:
            rgba: self.color
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, dp(8)
            width: dp(1)

<LabelButton@ThemedLabelButton>:
    disable_ripple_effect: True
    background_color: (0,0,0,0)



<ThemedIconButton@ThemedLabelButton>:
    icon_code: ''
    icon_size: sp(app.base_font_size + 10)
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    canvas:
        Color:
            rgba: self.background_color
        BorderImage:
            border:  self.border
            pos: self.pos
            size: self.size
            source: self.state_image if not root.disabled else self.disabled_image
    IconLabel:
        id: icon
        icon_code: root.icon_code
        font_size: root.icon_size
        text_size: self.size
        size: self.texture_size
        valign: 'middle'
        halign: 'center'
        size_hint: None, None
        pos_hint: {"center_x": .5, "center_y": .5}
        color: root.color

<-ImageButton>:
    state_image: self.background_normal if self.state == 'normal' else self.background_down
    background_color: app.colors['Primary'] if self.state == 'normal' else app.colors['Accent-One']
    orientation: 'vertical'
    padding: dp(5)
    spacing: dp(2)

    canvas:
        Color:
            rgba: self.background_color
        BorderImage:
            border:  [dp(8), dp(8), dp(8), dp(8)]
            pos: self.pos
            size: self.size
            source: root.state_image if not root.disabled else root.background_disabled

    Image:
        mipmap: True
        source: root.source



<SaveButton@ThemedIconButton>:
    icon_code: '\\ue161'
<CancelButton@ThemedIconButton>:
    icon_code: '\\ue5c9'
<OpenSettingsButton@ThemedIconButton>:
    icon_code: '\\ue8b9'
    background_color: (0,0,0,0)
    color: (1.0, 1.0, 1.0, 0.5)
""")


class ThemedButton(ButtonBehavior, BoxLayout, RippleMixin):
    """
    Base class for all MindRef themed buttons. By itself, it is an empty BoxLayout
    """

    background_normal = StringProperty(f"{texture_atlas}/bg_normal")
    background_down = StringProperty(f"{texture_atlas}/bg_down")
    background_disabled = StringProperty(f"{texture_atlas}/bg_disabled")
    background_color = ColorProperty()
    border = VariableListProperty()
    enable_ripple_effect = BooleanProperty(True)
    color = ColorProperty()

    def __init__(self, **kwargs: object):
        self._on_touch_down_plain = super().on_touch_down
        self._on_touch_move_plain = super().on_touch_move
        self._on_touch_up_plain = super().on_touch_up
        super().__init__(**kwargs)
        self.bind(enable_ripple_effect=self.toggle_ripple_effect)
        self.toggle_ripple_effect()

    def normalize_touch_pos(self, touch_x, touch_y):
        """
        Normalize touch position to texture coordinates.

        Kivy's origin point is the bottom left corner of the window.


        """
        return normalize_coordinates(
            touch_x,
            touch_y,
            self.x,
            self.y,
            self.height - self.border[0] - self.border[2],
            self.width - self.border[1] - self.border[3],
        )

    def toggle_ripple_effect(self, *_args):
        if self.enable_ripple_effect:
            self.on_touch_down = self._on_touch_down_ripple
            self.on_touch_move = self._on_touch_move
            self.on_touch_up = self._on_touch_up
        else:
            self.on_touch_down = self._on_touch_down_plain
            self.on_touch_move = self._on_touch_move_plain
            self.on_touch_up = self._on_touch_up_plain

    def _on_touch_down_ripple(self, touch):
        if super().on_touch_down(touch):
            self.touch = self.normalize_touch_pos(*touch.pos)
            self.no_touch_trigger.cancel()
            self.has_touch_trigger()
            return True
        return False

    def _on_touch_move(self, touch):
        if super().on_touch_move(touch):
            self.touch = self.normalize_touch_pos(*touch.pos)
            return True
        return False

    def _on_touch_up(self, touch):
        super().on_touch_up(touch)
        self.has_touch_trigger.cancel()
        self.no_touch_trigger()
        return True


class ThemedLabelButton(ThemedButton):
    """Extends ThemedButton to add a label"""

    text = StringProperty()

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)


class ContainedLabelButton(ThemedLabelButton):
    """Renders a button without a background, but draws a rectangle border"""

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)


class LabelButton(ThemedLabelButton):
    """Renders the most basic"""

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)


class LoadingButtonMixin:
    mutation: Mutation

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)

    def get_is_loading(self):
        """
        Check if the mutation is pending.
        """
        return self.mutation.is_mutating

    is_loading = AliasProperty(get_is_loading, rebind=True)


class ThemedIconButton(ThemedLabelButton):
    """Extends ThemedLabelButton by replacing BaseLabel with IconLabel"""

    icon_code = StringProperty()
    icon_size = NumericProperty()

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)


class ImageButton(ThemedButton):
    source = StringProperty()

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
