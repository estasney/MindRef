_INTENT_CLS = None


def _get_intent_cls():
    global _INTENT_CLS  # noqa: PLW0603
    if _INTENT_CLS is None:
        from jnius import autoclass

        _INTENT_CLS = autoclass("android.content.Intent")
    return _INTENT_CLS


def get_intent_cls():
    return _get_intent_cls()
