"""
Hand-written stub for the compiled `kivy.properties` Cython module
(pyright's stub generator produces an empty file for it).

Written against kivy 2.3.1 source: kivy/properties.pyx.

`Property[T]` models the descriptor protocol: class-level access returns the
property object, instance access returns `T`. Fully signed so far:
`BooleanProperty`, `ObjectProperty`, `ConfigParserProperty`; the rest are
declared with their trivially-correct value types. For properties whose value
type cannot be inferred from the constructor (`ObjectProperty`,
`ListProperty`), annotate the declaration site explicitly.

`ConfigParserProperty` accepts `Any` on assignment by design: incoming values
(config strings or user input) are converted through `val_type` before
storage, so `__get__` still returns `T`.

Note on `allownone=True`: the value type must carry `| None` in the
annotation; the runtime flag alone does not widen `T`.
"""

from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar, overload

from kivy.config import ConfigParser
from kivy.event import EventDispatcher

__all__ = (
    "Property",
    "NumericProperty",
    "StringProperty",
    "ListProperty",
    "ObjectProperty",
    "BooleanProperty",
    "BoundedNumericProperty",
    "OptionProperty",
    "ReferenceListProperty",
    "AliasProperty",
    "DictProperty",
    "VariableListProperty",
    "ConfigParserProperty",
    "ColorProperty",
)

T = TypeVar("T")

class PropertyStorage: ...
class ObservableList(list[Any]): ...
class ObservableDict(dict[Any, Any]): ...

class Property(Generic[T]):
    defaultvalue: T
    def __init__(
        self,
        defaultvalue: T,
        *,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: T = ...,
        errorhandler: Callable[[Any], T] | None = None,
        comparator: Callable[[T, T], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    @property
    def name(self) -> str: ...
    def __set_name__(self, owner: type[Any], name: str) -> None: ...
    @overload
    def __get__(self, obj: None, objtype: type[Any] | None = None) -> Self: ...
    @overload
    def __get__(self, obj: EventDispatcher, objtype: type[Any] | None = None) -> T: ...
    def __set__(self, obj: EventDispatcher, val: T) -> None: ...
    def get(self, obj: EventDispatcher) -> T: ...
    def set(self, obj: EventDispatcher, value: T) -> bool: ...
    def bind(self, obj: EventDispatcher, observer: Callable[..., Any]) -> None: ...
    def unbind(
        self, obj: EventDispatcher, observer: Callable[..., Any], stop_on_first: int = 0
    ) -> None: ...
    def fbind(
        self,
        obj: EventDispatcher,
        observer: Callable[..., Any],
        ref: int,
        largs: tuple[Any, ...] = ...,
        kwargs: dict[str, Any] = ...,
    ) -> int: ...
    def funbind(
        self,
        obj: EventDispatcher,
        observer: Callable[..., Any],
        largs: tuple[Any, ...] = ...,
        kwargs: dict[str, Any] = ...,
    ) -> None: ...
    def unbind_uid(self, obj: EventDispatcher, uid: int) -> None: ...
    def set_name(self, obj: EventDispatcher, name: str) -> None: ...
    def link(self, obj: EventDispatcher, name: str) -> PropertyStorage: ...
    def link_deps(self, obj: EventDispatcher, name: str) -> None: ...
    def link_eagerly(self, obj: EventDispatcher) -> PropertyStorage | None: ...
    def dispatch(self, obj: EventDispatcher) -> None: ...

class BooleanProperty(Property[bool]):
    def __init__(
        self,
        defaultvalue: bool = True,
        *,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: bool = ...,
        errorhandler: Callable[[Any], bool] | None = None,
        comparator: Callable[[bool, bool], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...

# The classes below are placeholders pending full signatures: value types are
# the trivially-correct ones, constructors are permissive.

class NumericProperty(Property[float]):
    def __init__(self, defaultvalue: Any = 0, **kw: Any) -> None: ...

class StringProperty(Property[str]):
    def __init__(self, defaultvalue: Any = "", **kw: Any) -> None: ...

class ListProperty(Property[list[T]]):
    def __init__(self, defaultvalue: Any = ..., **kw: Any) -> None: ...

class ObjectProperty(Property[T]):
    def __init__(
        self,
        defaultvalue: T | None = None,
        rebind: bool = False,
        *,
        allownone: bool = False,
        baseclass: type[Any] | None = None,
        force_dispatch: bool = False,
        errorvalue: T = ...,
        errorhandler: Callable[[Any], T] | None = None,
        comparator: Callable[[T, T], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...

class BoundedNumericProperty(Property[float]):
    def __init__(self, *largs: Any, **kw: Any) -> None: ...

class OptionProperty(Property[Any]):
    def __init__(self, *largs: Any, **kw: Any) -> None: ...

class ReferenceListProperty(Property[list[Any]]):
    def __init__(self, *largs: Any, **kw: Any) -> None: ...

class AliasProperty(Property[Any]):
    def __init__(self, *largs: Any, **kw: Any) -> None: ...

class DictProperty(Property[dict[Any, Any]]):
    def __init__(
        self, defaultvalue: Any = ..., rebind: bool = False, **kw: Any
    ) -> None: ...

class VariableListProperty(Property[list[float]]):
    def __init__(
        self, defaultvalue: Any = None, length: int = 4, **kw: Any
    ) -> None: ...

class ConfigParserProperty(Property[T]):
    def __init__(
        self,
        defaultvalue: T,
        section: str,
        key: str,
        config: str | ConfigParser | None,
        *,
        val_type: Callable[[Any], T] | None = None,
        verify: Callable[[T], bool] | None = None,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: T = ...,
        errorhandler: Callable[[Any], T] | None = None,
        comparator: Callable[[T, T], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    def __set__(self, obj: EventDispatcher, val: Any) -> None: ...
    def set(self, obj: EventDispatcher, value: Any) -> bool: ...
    def set_config(self, config: ConfigParser | None) -> None: ...

class ColorProperty(Property[list[float]]):
    def __init__(self, defaultvalue: Any = 0, **kw: Any) -> None: ...
