"""
Hand-written stub for pyjnius.

pyjnius is a Cython extension that python-for-android builds against the
Android NDK. It is never installed on the desktop, so no stub can be generated
from it. This stub covers only the names MindRef imports.

Source of truth: https://github.com/kivy/pyjnius
"""

from collections.abc import Callable, Sequence
from typing import Any, ClassVar

__all__ = ["PythonJavaClass", "autoclass", "java_method"]

def autoclass(
    clsname: str, include_protected: bool = ..., include_private: bool = ...
) -> Any:
    """
    Build a Python class from a fully qualified Java class name.

    The class is synthesized by reflection at call time, so its members cannot
    be known statically. Give the result a Protocol annotation at the call site
    to describe the members you use.
    """
    ...

class java_method:
    """
    Decorator that binds a Python method to a Java method signature.

    The decorator returns the function unchanged. It records the signature on
    the function so that PythonJavaClass can dispatch Java calls to it.

    `name` is the Java method name. It defaults to the Python method name.
    """

    signature: str
    name: str | None

    def __init__(self, signature: str, name: str | None = ...) -> None: ...
    def __call__[F: Callable[..., Any]](self, f: F) -> F: ...

class PythonJavaClass:
    """
    Base class that implements one or more Java interfaces in Python.

    A subclass lists the interfaces it implements in `__javainterfaces__`, and
    decorates each implementing method with `java_method`. Set
    `__javacontext__` to "app" to resolve the interfaces with the application
    class loader. It defaults to "system" when not set.
    """

    __javainterfaces__: ClassVar[Sequence[str]]
    j_self: Any

    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def invoke(self, method: Any, *args: Any) -> Any: ...
