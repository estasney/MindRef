"""
Hand-written stub for the compiled `kivy.properties` Cython module
(pyright's stub generator produces an empty file for it).

Written against kivy 2.3.1 source: kivy/properties.pyx.

`Property[T]` models the descriptor protocol: class-level access returns the
property object, instance access returns `T`. All concrete property classes
are fully signed. For properties whose value type cannot be inferred from the
constructor (`ObjectProperty()`, bare `ListProperty()`), annotate the
declaration site explicitly.

`__get__`/`__set__` accept any `obj`, not just `EventDispatcher`: Kivy's
behavior-mixin idiom declares properties on plain classes that are only ever
mixed into widgets. The explicit `get`/`set`/`bind` methods keep the
`EventDispatcher` bound.

`StringProperty` is generic over `str` vs `str | None`, selected by the
`allownone` overloads: `StringProperty(None, allownone=True)` reads as
`str | None`; `StringProperty(None)` without the flag is a genuine runtime
`ValueError` and is rejected.

`ConfigParserProperty` accepts `Any` on assignment by design: incoming values
(config strings or user input) are converted through `val_type` before
storage, so `__get__` still returns `T`.

Note on `allownone=True` (except `StringProperty`, see above): the value type
must carry `| None` in the annotation; the runtime flag alone does not
widen `T`.

`NumericValue` mirrors what Kivy's numeric conversion accepts on assignment:
a number, a unit string (`"10dp"`), or a `(value, unit)` tuple; reads always
come back as plain numbers.
"""

from collections.abc import Callable, Iterable, Sequence
from typing import Any, Generic, Literal, Self, TypeVar, overload

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
K = TypeVar("K")
V = TypeVar("V")

type NumericValue = float | str | tuple[float, str]

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
    def __get__(self, obj: object, objtype: type[Any] | None = None) -> T: ...
    def __set__(self, obj: object, val: T) -> None: ...
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

class NumericProperty(Property[float]):
    def __init__(
        self,
        defaultvalue: NumericValue = 0,
        *,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: NumericValue = ...,
        errorhandler: Callable[[object], NumericValue] | None = None,
        comparator: Callable[[float, float], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    def __set__(self, obj: object, val: NumericValue) -> None: ...
    def set(self, obj: EventDispatcher, value: NumericValue) -> bool: ...
    def get_format(self, obj: EventDispatcher) -> str: ...

class StringProperty(Property[T]):
    @overload
    def __init__(
        self: StringProperty[str],
        defaultvalue: str = "",
        *,
        allownone: Literal[False] = False,
        force_dispatch: bool = False,
        errorvalue: str = ...,
        errorhandler: Callable[[object], str] | None = None,
        comparator: Callable[[str, str], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    @overload
    def __init__(
        self: StringProperty[str | None],
        defaultvalue: str | None = None,
        *,
        allownone: Literal[True],
        force_dispatch: bool = False,
        errorvalue: str = ...,
        errorhandler: Callable[[object], str] | None = None,
        comparator: Callable[[str, str], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...

class ListProperty(Property[list[T]]):
    def __init__(
        self,
        defaultvalue: list[T] = [],
        *,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: list[T] = ...,
        errorhandler: Callable[[object], list[T]] | None = None,
        comparator: Callable[[list[T], list[T]], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...

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
    def __init__(
        self,
        defaultvalue: float = 0,
        *,
        min: float = ...,
        max: float = ...,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: float = ...,
        errorhandler: Callable[[object], float] | None = None,
        comparator: Callable[[float, float], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    def set_min(self, obj: EventDispatcher, value: float | None) -> None: ...
    def get_min(self, obj: EventDispatcher) -> float | None: ...
    def set_max(self, obj: EventDispatcher, value: float | None) -> None: ...
    def get_max(self, obj: EventDispatcher) -> float | None: ...

class OptionProperty(Property[T]):
    def __init__(
        self,
        defaultvalue: T,
        *,
        options: Iterable[T],
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: T = ...,
        errorhandler: Callable[[object], T] | None = None,
        comparator: Callable[[T, T], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    @property
    def options(self) -> list[T]: ...

class ReferenceListProperty(Property[list[T]]):
    def __init__(
        self,
        *largs: Property[T],
        allownone: bool = False,
        force_dispatch: bool = False,
        comparator: Callable[[list[T], list[T]], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    def __set__(self, obj: object, val: Sequence[T]) -> None: ...
    def set(self, obj: EventDispatcher, value: Sequence[T]) -> bool: ...
    def setitem(
        self, obj: EventDispatcher, key: int | slice, value: T | Sequence[T]
    ) -> None: ...

class AliasProperty(Property[T]):
    def __init__(
        self,
        getter: Callable[..., T],
        setter: Callable[..., bool | None] | None = None,
        rebind: bool = False,
        watch_before_use: bool = True,
        *,
        bind: Sequence[str] = ...,
        cache: bool = False,
        force_dispatch: bool = False,
    ) -> None: ...
    def trigger_change(self, obj: EventDispatcher, value: object) -> None: ...

class DictProperty(Property[dict[K, V]]):
    def __init__(
        self,
        defaultvalue: dict[K, V] = ...,
        rebind: bool = False,
        *,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: dict[K, V] = ...,
        errorhandler: Callable[[object], dict[K, V]] | None = None,
        comparator: Callable[[dict[K, V], dict[K, V]], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...

class VariableListProperty(Property[list[float]]):
    def __init__(
        self,
        defaultvalue: NumericValue | Sequence[NumericValue] | None = None,
        length: Literal[2, 4] = 4,
        *,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: list[float] = ...,
        errorhandler: Callable[[object], list[float]] | None = None,
        comparator: Callable[[list[float], list[float]], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    def __set__(
        self, obj: object, val: NumericValue | Sequence[NumericValue]
    ) -> None: ...
    def set(
        self, obj: EventDispatcher, value: NumericValue | Sequence[NumericValue]
    ) -> bool: ...

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
    def __set__(self, obj: object, val: Any) -> None: ...
    def set(self, obj: EventDispatcher, value: Any) -> bool: ...
    def set_config(self, config: ConfigParser | None) -> None: ...

class ColorProperty(Property[list[float]]):
    def __init__(
        self,
        defaultvalue: str | Sequence[float] = ...,
        *,
        allownone: bool = False,
        force_dispatch: bool = False,
        errorvalue: str | Sequence[float] = ...,
        errorhandler: Callable[[object], str | Sequence[float]] | None = None,
        comparator: Callable[[list[float], list[float]], bool] | None = None,
        deprecated: bool = False,
    ) -> None: ...
    def __set__(self, obj: object, val: str | Sequence[float]) -> None: ...
    def set(self, obj: EventDispatcher, value: str | Sequence[float]) -> bool: ...
