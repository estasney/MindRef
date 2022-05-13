from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from registry import Registry


class LazyLoaded:
    def __init__(self, default: Optional[Callable] = None):
        self.default = default if default is None else default()

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"
        setattr(owner, self.private_name, self.default)

    def __get__(self, obj, objtype=None):
        value = getattr(obj, self.private_name)
        if value == self.default:
            value = getattr(obj, self.loader)()
            setattr(obj, self.private_name, value)
        return value

    def __set__(self, instance, value):
        if not value:
            setattr(instance, self.private_name, self.default)
        else:
            setattr(instance, self.private_name, value)

    def __call__(self, func):
        """Register a loader function"""
        self.loader = func.__name__
        return func


class LazyRegistry:
    registry: Optional["Registry"] = None

    def __get__(self, instance, owner):
        if self.registry:
            return self.registry
        try:
            from utils.registry import app_registry

            self.registry = app_registry
            return self.registry
        except ValueError:
            return None
