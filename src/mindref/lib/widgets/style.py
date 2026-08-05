from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

Builder.load_string("""
<BaseLabel>:
    font_size: sp(app.base_font_size)
    font_family: app.fonts['default']
    mipmap: True

<IconLabel>:
    font_size: sp(app.base_font_size)
    markup: True
    mipmap: True
    text: f'[font={app.fonts["icons"]}]{self.icon_code}[/font]'

<NavigateNext@IconLabel>:
    icon_code: "\\ue409"

<NavigateBefore@IconLabel>:
    icon_code: "\\ue408"

<StyledTextInput@TextInput>:
    input_type: 'text'
    size_hint_y: None
    height: self.minimum_height
    background_normal: ''
    background_active: ''
    background_color: 0, 0, 0, 0
    cursor_color: app.colors['Gray-600']
    foreground_color: 1,1,1,1

    canvas.after:
        Color:
            rgba: [*app.colors['Gray-800'][:3], 0.1]
        RoundedRectangle:
            pos: [self.x, self.y - dp(8)]
            size: [self.width, self.height+(2*dp(8))]
            radius: [dp(4), dp(4), dp(4), dp(4)]
        Color:
            rgba: [*app.colors['Gray-800'][:3], 0.2] if not self.focus else [*app.colors['Gray-800'][:3], 0.4]
        Line:
            points: [self.x, self.y - dp(8), self.x + self.width, self.y - dp(8)]
            width: dp(1)
""")


class BaseLabel(Label): ...


class IconLabel(BaseLabel):
    icon_code = StringProperty()


class StyledTextInput(TextInput): ...
