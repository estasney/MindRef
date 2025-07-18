_KIVY_ACTIVITY_CLASS = None


def _get_kivy_activity_cls():
    global _KIVY_ACTIVITY_CLASS  # noqa: PLW0603
    if _KIVY_ACTIVITY_CLASS is None:
        from jnius import autoclass

        _KIVY_ACTIVITY_CLASS = autoclass("org.kivy.android.PythonActivity")
    return _KIVY_ACTIVITY_CLASS


def get_kivy_activity():
    cls = _get_kivy_activity_cls()
    return cls().mActivity
