from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mindref.lib.adapters.brokered.android.types import IntentProtocol


@cache
def get_intent_cls() -> type[IntentProtocol]:
    from jnius import autoclass

    return autoclass("android.content.Intent")
