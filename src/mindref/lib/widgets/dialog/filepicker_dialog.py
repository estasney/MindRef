from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.floatlayout import FloatLayout

Builder.load_string("""
#:import ThemedLabelButton mindref.lib.widgets.buttons.buttons



<LoadDialog>:
    chooser: file_chooser
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: 'vertical'
        FileChooserIconView:
            id: file_chooser
            dirselect: root.dirselect
            filters: root.filters
        BoxLayout:
            size_hint_y: None
            height: self.minimum_height
            orientation: 'horizontal'
            ThemedLabelButton:
                text: 'OK'
                disabled: not file_chooser.selection
                on_release: root.dispatch('on_button_event', 'accept', file_chooser.path, file_chooser.selection)
            ThemedLabelButton:
                text: 'Cancel'
                on_release: root.dispatch('on_button_event', 'cancel')


<SaveDialog>:
    chooser: file_chooser
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: 'vertical'
        FileChooserIconView:
            id: file_chooser
            dirselect: root.dirselect
            on_selection: text_input.text = self.selection and self.selection[0] or ''
            filters: root.filters
        TextInput:
            id: text_input:
            size_hint_y: None
            height: sp(app.base_font_size * 2)
            multiline: False
            input_type: 'text'
        BoxLayout:
            orientation: 'horizontal'
            ThemedLabelButton:
                text: 'Save'
                on_release: root.dispatch('on_button_event', 'accept', file_chooser.path, text_input.text)
            ThemedLabelButton:
                text: 'Cancel'
                on_release: root.dispatch('on_button_event', 'cancel')


""")


class PickerDialog(FloatLayout):
    filters = ListProperty()
    dirselect = BooleanProperty()
    on_accept = ObjectProperty()
    on_cancel = ObjectProperty()
    start_folder = StringProperty()
    chooser = ObjectProperty()

    def __init__(self, on_accept, on_cancel, **kwargs):
        super().__init__(**kwargs)
        self.on_accept = on_accept
        self.on_cancel = on_cancel
        self.register_event_type("on_button_event")

    def on_chooser(self, *_args):
        if self.start_folder:
            self.chooser.path = self.start_folder

    def on_button_event(self, event, *args):
        Logger.info(f"{type(self).__name__}: on_button_event - {event} - {args}")
        if event == "accept":
            _, file_path = args
            self.on_accept(file_path[0])
        else:
            self.on_cancel(*args)
        return True


class LoadDialog(PickerDialog):
    chooser = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SaveDialog(PickerDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
