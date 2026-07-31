from collections.abc import Callable

type ClockCallback = Callable[[float], object]

class ClockNotRunningError(RuntimeError): ...

class ClockEvent:
    next: ClockEvent | None
    prev: ClockEvent | None
    cid: object
    clock: CyClockBase
    loop: int
    weak_callback: object
    callback: ClockCallback | None
    timeout: float
    clock_ended_callback: ClockCallback | None
    weak_clock_ended_callback: object
    release_ref: int

    def __init__(
        self,
        clock: CyClockBase,
        loop: int,
        callback: ClockCallback,
        timeout: float,
        starttime: float,
        cid: object = None,
        trigger: int = False,
        clock_ended_callback: ClockCallback | None = None,
        release_ref: bool = True,
        **kwargs: object,
    ) -> None: ...
    def __call__(self, *largs: object) -> None: ...
    @property
    def is_triggered(self) -> bool: ...
    def get_callback(self) -> ClockCallback | None: ...
    def get_clock_ended_callback(self) -> ClockCallback | None: ...
    def cancel(self) -> None: ...
    def release(self) -> None: ...
    def tick(self, curtime: float) -> bool: ...

class FreeClockEvent(ClockEvent):
    free: int

    def __init__(self, free: int, *largs: object, **kwargs: object) -> None: ...

class CyClockBase:
    max_iteration: int
    clock_resolution: float
    has_started: int
    has_ended: int

    def __init__(self, **kwargs: object) -> None: ...
    def get_resolution(self) -> float: ...
    def create_lifecycle_aware_trigger(
        self,
        callback: ClockCallback,
        clock_ended_callback: ClockCallback,
        timeout: float = 0,
        interval: bool = False,
        release_ref: bool = True,
    ) -> ClockEvent: ...
    def create_trigger(
        self,
        callback: ClockCallback,
        timeout: float = 0,
        interval: bool = False,
        release_ref: bool = True,
    ) -> ClockEvent: ...
    def schedule_lifecycle_aware_del_safe(
        self, callback: Callable[[], object], clock_ended_callback: Callable[[], object]
    ) -> None: ...
    def schedule_del_safe(self, callback: Callable[[], object]) -> None: ...
    def schedule_once(
        self, callback: ClockCallback, timeout: float = 0
    ) -> ClockEvent: ...
    def schedule_interval(
        self, callback: ClockCallback, timeout: float
    ) -> ClockEvent: ...
    def unschedule(
        self, callback: ClockCallback | ClockEvent, all: bool = True
    ) -> None: ...
    def get_min_timeout(self) -> float: ...
    def get_events(self) -> list[ClockEvent]: ...
    def get_before_frame_events(self) -> list[ClockEvent]: ...
    def on_schedule(self, event: ClockEvent) -> None: ...

class CyClockBaseFree(CyClockBase):
    def create_lifecycle_aware_trigger_free(
        self,
        callback: ClockCallback,
        clock_ended_callback: ClockCallback,
        timeout: float = 0,
        interval: bool = False,
        release_ref: bool = True,
    ) -> FreeClockEvent: ...
    def create_trigger_free(
        self,
        callback: ClockCallback,
        timeout: float = 0,
        interval: bool = False,
        release_ref: bool = True,
    ) -> FreeClockEvent: ...
    def schedule_once_free(
        self, callback: ClockCallback, timeout: float = 0
    ) -> FreeClockEvent: ...
    def schedule_interval_free(
        self, callback: ClockCallback, timeout: float
    ) -> FreeClockEvent: ...
    def get_min_free_timeout(self) -> float: ...
