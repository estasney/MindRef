from kivy.parser import parse_color

THEME_COLORS = {
    "White": (1, 1, 1),
    "Black": (0, 0, 0),
    "RichBlack": parse_color("#161D28"),
    "Gray-100": parse_color("#f5f5f5"),
    "Gray-200": parse_color("#dadbda"),
    "Gray-300": parse_color("#c1c1c1"),
    "Gray-400": parse_color("#a7a7a7"),
    "Gray-500": parse_color("#8f8f8f"),
    "Gray-600": parse_color("#777777"),
    "Gray-700": parse_color("#606060"),
    "Gray-800": parse_color("#4a4a4a"),
    "Gray-900": parse_color("#353535"),
    "Codespan": parse_color("#00000026"),
    "Keyboard": parse_color("#ffffffaf"),
    "KeyboardShadow": parse_color("#656565ff"),
    "Primary": parse_color("#37464f"),
    "Dark": parse_color("#1f1f1f"),
    "Accent-One": parse_color("#388fe5"),
    "Accent-Two": parse_color("#56e39f"),
    "Warn": parse_color("#fa1919"),
}
