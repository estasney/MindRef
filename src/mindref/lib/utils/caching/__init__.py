from functools import wraps
from typing import Callable, Optional, TypeVar, Hashable, TYPE_CHECKING

from kivy.cache import Cache

if TYPE_CHECKING:
    from typing import ParamSpec

    POuter = ParamSpec("POuter")
    PInner = ParamSpec("PInner")
    TInner = TypeVar("TInner")
    KeyedCallable = Callable[POuter, Hashable]
    InnerCallable = Callable[PInner, TInner]


def kivy_cache(
    cache_name: str,
    key_func: "KeyedCallable",
    limit: Optional[int] = None,
    timeout: Optional[int] = None,
) -> "InnerCallable":
    """
    Used as decorator to wrap a function in a Kivy Cache

    Parameters
    -----------
    cache_name: str
        Cache namespace that is accessed with `Cache.get(cache_name, key)`
    key_func: Callable[..., str]
        Function that accepts *args, **kwargs that generates a key to lookup in cache
    limit : Passed to Cache.Register
    timeout
    """

    categories_seen = getattr(kivy_cache, "categories_seen", set())
    if cache_name not in categories_seen:
        Cache.register(cache_name, limit=limit, timeout=timeout)
        categories_seen.add(cache_name)
    setattr(kivy_cache, "categories_seen", categories_seen)

    def dec_kivy_cache(func: "InnerCallable"):
        @wraps(func)
        def wrapped_func(*args: "PInner.args", **kwargs: "PInner.kwargs") -> "TInner":
            key = key_func(**kwargs)
            cached_result: "TInner" = Cache.get(cache_name, key)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            Cache.append(cache_name, key, result)
            return result

        return wrapped_func

    return dec_kivy_cache


def cache_key_text_extents(**kwargs) -> str:
    """Generate key for 'text_extents' cache"""
    label = kwargs.get("label")
    text = kwargs.get("text")
    opts = label.options
    return f"{text}-{opts['font_size']}-{opts['font_family']}"


def cache_key_text_contrast(*_args, **kwargs) -> tuple[tuple, int, Optional[tuple]]:
    """Generate key for 'text_contrast'"""
    background_color = kwargs.get("background_color")
    threshold = kwargs.get("threshold")
    highlight_color = kwargs.get("highlight_color")
    return (
        tuple(background_color),
        int(threshold),
        tuple(highlight_color) if highlight_color else None,
    )


def cache_key_color_norm(*_args, **kwargs) -> tuple:
    return tuple(kwargs.get("color"))


def cache_key_note(*_args, **kwargs) -> str:
    content_data = kwargs.get("content_data")
    parent = kwargs.pop("parent")
    return f"{content_data['filepath']}-{content_data['text']}-{hash(parent)}"
