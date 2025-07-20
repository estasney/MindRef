from concurrent.futures import ThreadPoolExecutor

_POOL: ThreadPoolExecutor | None = None


def get_pool() -> ThreadPoolExecutor:
    global _POOL  # noqa: PLW0603
    if _POOL is None:
        _POOL = ThreadPoolExecutor(max_workers=4)
    return _POOL
