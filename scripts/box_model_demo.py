import sys
from pathlib import Path

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

sys.path.append(str(Path.cwd().parent / "mindref" / "widgets" / "box_model"))
print(sys.path)
from kivy import Config
from kivy.app import App
from box import Box


class BoxDemoApp(App):
    def build(self):
        parent = BoxLayout()
        for i in range(3):
            cbox = Box(border_size=1, margin=25, box_padding=25)
            cbox.add_widget_content(Label(text=str(i)))
            parent.add_widget(cbox)

        return parent


if __name__ == "__main__":
    Config.set("modules", "inspector", "")
    BoxDemoApp().run()
