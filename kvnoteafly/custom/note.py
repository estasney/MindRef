from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from custom.code import ContentCode
from custom.keyboard import ContentKeyboard
from custom.rst import ContentRST
from db import NoteType
from utils import import_kv

import_kv(__file__)


class Note(BoxLayout):
    note_title = ObjectProperty()
    note_content = ObjectProperty()
    note_tags = ObjectProperty()

    def set_note_content(self, note_data: dict):
        title_data = {
            "title": note_data['title']
            }

        content_data = {
            "text":      note_data['text'],
            "keys_str":  note_data['keys_str'],
            "note_type": note_data['note_type'],
            "code_lexer": note_data.get('code_lexer')
            }

        self.note_title.set(title_data)
        self.note_content.set(content_data)


class NoteContent(BoxLayout):

    def set(self, content_data: dict):

        self.clear_widgets()

        if content_data['note_type'] == NoteType.TEXT_NOTE.name:
            self._set_text(content_data)
        elif content_data['note_type'] == NoteType.KEYBOARD_NOTE.name:
            self._set_keyboard(content_data)
        elif content_data['note_type'] == NoteType.CODE_NOTE.name:
            self._set_rst(content_data)

    def _set_text(self, content_data: dict):
        self.add_widget(
                ContentRST(content_data=content_data)
                )

    def _set_keyboard(self, content_data: dict):
        self.add_widget(
                ContentKeyboard(content_data=content_data)
                )

    def _set_rst(self, content_data: dict):
        self.add_widget(
                ContentCode(content_data=content_data)
                )


class NoteTitle(BoxLayout):
    title_text = StringProperty()
    play_state = StringProperty()
    button_bar = ObjectProperty()
    play_state_button = ObjectProperty()

    def __init__(self, **kwargs):
        if 'note_title' in kwargs:
            self.title_text = kwargs.pop('note_title')
        super().__init__(**kwargs)

    def set(self, title_data):
        self.title_text = title_data['title']

    def on_play_state(self, instance, value):
        pass


class NoteTags(BoxLayout):
    pass
