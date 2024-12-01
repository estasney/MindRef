from enum import StrEnum


class DisplayState(StrEnum):
    CHOOSE = "choose"
    DISPLAY = "display"
    LIST = "list"
    EDIT = "edit"
    ADD = "add"
    ERROR = "error"
    CATEGORY_EDITOR = "category_editor"
