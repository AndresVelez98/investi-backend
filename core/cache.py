"""
core/cache.py — Simple TTL in-memory cache decorator

Uses per-key locking so that a slow external call (yfinance, LLM API) for
one cache key does not block threads serving a different key.
"""
import time
import functools
from threading import Lock

_cache: dict = {}
_key_locks: dict = {}
_meta_lock = Lock()  # protects _key_locks itself


def _get_key_lock(key) -> Lock:
    with _meta_lock:
        if key not in _key_locks:
            _key_locks[key] = Lock()
        return _key_locks[key]


def ttl_cache(ttl: int = 60):
    """Decorator that caches a function's return value for `ttl` seconds.

    Per-key locking ensures only one thread executes the underlying function
    for a given key while others wait, without blocking unrelated keys.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__qualname__, args, tuple(sorted(kwargs.items())))
            key_lock = _get_key_lock(key)
            with key_lock:
                entry = _cache.get(key)
                if entry and (time.monotonic() - entry["ts"]) < ttl:
                    return entry["value"]
                value = func(*args, **kwargs)
                _cache[key] = {"value": value, "ts": time.monotonic()}
                return value
        return wrapper
    return decorator
