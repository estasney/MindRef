from kivy import Logger
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    StringProperty,
    AliasProperty,
    ObjectProperty,
    NumericProperty,
)
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv

import_kv(__file__)


class TextField(BoxLayout):
    text = StringProperty()
    helper_text = StringProperty()
    error_message = StringProperty()
    w_text_input = ObjectProperty()
    w_error_message_label = ObjectProperty()
    _touched_state = NumericProperty(0)

    """
    Attributes
    ----------
    text: str
        Text of the text input
    helper_text: str
        Text to be displayed above the text input, as a label
    error_message: str
        Optional text to be displayed below the text input, to indicate an error
    w_text_input: TextInput
        The TextInput widget. We keep a reference to it so we can reset its state
    w_error_message_label: Label
        The Label widget that displays the error message. We explicitly use its __self__ attribute to avoid garbage collection
    _touched_state: int
        Bitwise state of the touched property. 
            0b00 = Had focus - False, Current Focus - False. This is the default state 
            0b01 = Had focus - False, Current Focus - True. This is the state when the user clicks on the text input
            0b10 = Had focus - True, Current Focus - False. This is the state when the user clicks away from the text input.
            0b11 = Had focus - True, Current Focus - True. This should never happen          
        We are detecting what is analogous to a falling edge in a circuit.  
    
    """

    def get_touched(self):
        """We are detecting what is analogous to a falling edge in a circuit.
        So when _touch_state is 0b10, *and* text we return True"""
        return self._touched_state == 0b10 and self.text != ""

    def set_touched(self, value: bool):
        """Ideally, we wouldn't use this, but it's implemented to easily reset the state from a higher level widget
        without needing to know the implementation of the bitwise state."""

        # If we force a reset, we reset the state to 0b00
        # Otherwise, we set the _touched_state to 0b10 to reflect the falling edge
        self._touched_state = 0b10 if value else 0b00
        return True

    touched = AliasProperty(
        getter=get_touched,
        setter=set_touched,
        bind=("text", "_touched_state"),
        cache=True,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.prepare, timeout=0)

    def prepare(self, *_args):
        """
        Parameters
        ----------
        _args

        Notes
        -----
        This should be called immediately after the widget is instantiated. We do this in the __init__ method,
            but we defer it to the next frame.

        Why do we need this?
            We want to include the error message label in the kv file, but we don't want it to be
            immediately visible. We want to show it only when there is an error.
            So we need to hide it initially by removing
            it from the parent widget.
        """
        self.remove_widget(self.w_error_message_label)

    def on_text(self, _instance, _val):
        """
        We've bound to TextInput's on_text event in the .kv file.
        If we have an error message, we want to hide it when the user starts typing or clears their input.
        """
        self.error_message = ""
        return True

    def touch_handler(self, focused: bool):
        """
        This implements the falling edge detection. Text input's on_focus event is bound to this method in the .kv file.

        """
        # We shift the _touched_state to the left by 1 bit
        # To ensure this dispatches correctly, we want to avoid assignment operators on the property
        result = self._touched_state << 1
        # We shift what is now the least significant bit to the most significant bit
        result |= focused
        # We truncate the result to 2 bits
        result &= 0b11
        self._touched_state = result
        return True

    def on_error_message(self, _instance, value: str):
        """
        If we have an error message, we want to show it. Conversely, if we don't have an error message,
        we want to hide it.
        """
        if value:
            self.add_widget(self.w_error_message_label)
        else:
            self.remove_widget(self.w_error_message_label)
        return True

    def clear(self):
        """
        Clears the widget state

        Notes
        -----
        Since our text state is bound to our w_text_input's text state, we expose a method to clear the text input
        from w_text_input without needing to know the implementation details of the widget.
        """

        self.w_text_input.text = ""
        self.error_message = ""
        self.touched = False

        return True
