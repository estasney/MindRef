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


def kivy_cache(cache_name: str, key_func: "KeyedCallable") -> "InnerCallable":
    """
    Used as decorator to wrap a function in a Kivy Cache

    Parameters
    -----------
    cache_name: str
        Cache namespace that is accessed with `Cache.get(cache_name, key)`
    key_func: Callable[..., str]
        Function that accepts *args, **kwargs that generates a key to lookup in cache
    """

    def dec_kivy_cache(func: "InnerCallable"):
        @wraps(func)
        def wrapped_func(**kwargs: "PInner.kwargs") -> "TInner":
            key = key_func(**kwargs)
            cached_result: "TInner" = Cache.get(cache_name, key)
            if cached_result is not None:
                return cached_result
            result = func(**kwargs)
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


def cache_key_text_contrast(*args, **kwargs) -> tuple[tuple, int, Optional[tuple]]:
    """Generate key for 'text_contrast'"""
    background_color = kwargs.get("background_color")
    threshold = kwargs.get("threshold")
    highlight_color = kwargs.get("highlight_color")
    return (
        tuple(background_color),
        int(threshold),
        tuple(highlight_color) if highlight_color else None,
    )


def cache_key_color_norm(*args, **kwargs) -> tuple:
    return tuple(kwargs.get("color"))


def cache_key_note(*args, **kwargs) -> str:
    content_data = kwargs.get("content_data")
    parent = kwargs.pop("parent")
    return f"{content_data['filepath']}-{content_data['text']}-{hash(parent)}"
