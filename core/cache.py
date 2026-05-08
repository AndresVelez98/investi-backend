"""
core/cache.py — Simple TTL in-memory cache decorator
"""
import time
import functools
from threading import Lock

_cache: dict = {}
_lock = Lock()


def ttl_cache(ttl: int = 60):
    """Decorator that caches a function's return value for `ttl` seconds."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__qualname__, args, tuple(sorted(kwargs.items())))
            with _lock:
                entry = _cache.get(key)
                if entry and (time.monotonic() - entry["ts"]) < ttl:
                    return entry["value"]
            value = func(*args, **kwargs)
            with _lock:
                _cache[key] = {"value": value, "ts": time.monotonic()}
            return value
        return wrapper
    return decorator
