from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import IntentProtocol


@cache
def get_intent_cls() -> "IntentProtocol":
    from jnius import autoclass

    return autoclass("android.content.Intent")
