"""Python decorators helpers."""

from __future__ import annotations

import functools
import inspect
import logging
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def _check_sync(func: Callable[..., object]) -> None:
    """Reject async functions."""

    if inspect.iscoroutinefunction(func):
        name = getattr(func, "__qualname__", repr(func))
        raise TypeError(f"{name} is async; these decorators support sync functions only.")


def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    """Debug-log each call to `func`, its return, and any exception it raises."""

    _check_sync(func)
    logger = logging.getLogger(getattr(func, "__module__", None) or __name__)
    name = getattr(func, "__qualname__", repr(func))

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.debug("Calling %s", name)
        try:
            result = func(*args, **kwargs)
        except BaseException as exc:
            logger.debug("%s raised %s", name, type(exc).__name__)
            raise
        logger.debug("%s returned", name)
        return result

    return wrapper


def measure_time(func: Callable[P, R]) -> Callable[P, R]:
    """Debug-log how long `func` took, even if it raised."""

    _check_sync(func)
    logger = logging.getLogger(getattr(func, "__module__", None) or __name__)
    name = getattr(func, "__qualname__", repr(func))

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()  # monotonic; unaffected by system clock changes
        try:
            return func(*args, **kwargs)
        finally:
            logger.debug("%s took %.3f s", name, time.perf_counter() - start)

    return wrapper


def retry(
    *,
    attempts: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (OSError,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry a function when it raises one of `exceptions`."""

    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    if delay < 0:
        raise ValueError("delay must be >= 0")
    if backoff < 1:
        raise ValueError("backoff must be >= 1")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        _check_sync(func)
        logger = logging.getLogger(getattr(func, "__module__", None) or __name__)
        name = getattr(func, "__qualname__", repr(func))

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            wait = delay
            for attempt in range(1, attempts):  # all but the last attempt
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    logger.warning(
                        "%s failed (attempt %d/%d): %r; retrying in %.2f s",
                        name, attempt, attempts, exc, wait,
                    )
                    time.sleep(wait)
                    wait *= backoff
            return func(*args, **kwargs)  # last attempt: errors propagate as-is

        return wrapper

    return decorator