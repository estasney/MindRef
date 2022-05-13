from registry import Registry

_APP_REGISTRY = None


def _load_registry():
    global _APP_REGISTRY
    if _APP_REGISTRY:
        return _APP_REGISTRY
    app_registry = Registry("app_registry")
    app_registry.add_topics(["note_files", "note_meta", "category_images"])
    _APP_REGISTRY = app_registry
    return _APP_REGISTRY


def __getattr__(name: str):
    if name == "app_registry":
        return _load_registry()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
