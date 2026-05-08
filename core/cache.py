"""
core/cache.py — Simple TTL in-memory cache decorator
"""
import time
import functools
from threading import Lock

_cache: dict = {}
_lock = Lock()


def ttl_cache(ttl: int = 60):
    """Decorator that caches a function's return value for `ttl` seconds.

    Uses double-checked locking to prevent thundering herd: if two threads
    arrive simultaneously after cache expiry, only one executes the function.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__qualname__, args, tuple(sorted(kwargs.items())))
            # Fast path: read under lock
            with _lock:
                entry = _cache.get(key)
                if entry and (time.monotonic() - entry["ts"]) < ttl:
                    return entry["value"]
                # Slow path: execute inside lock so only one thread calls func
                value = func(*args, **kwargs)
                _cache[key] = {"value": value, "ts": time.monotonic()}
                return value
        return wrapper
    return decorator
