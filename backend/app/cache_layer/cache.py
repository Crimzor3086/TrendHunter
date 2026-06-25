from datetime import datetime, timedelta, timezone
from typing import Any


class LocalTTLCache:
    def __init__(self) -> None:
        self._items: dict[str, tuple[datetime, Any]] = {}

    def set(self, key: str, value: Any, ttl_seconds: int = 120) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        self._items[key] = (expires_at, value)

    def get(self, key: str) -> Any | None:
        item = self._items.get(key)
        if item is None:
            return None

        expires_at, value = item
        if expires_at <= datetime.now(timezone.utc):
            self._items.pop(key, None)
            return None
        return value


class RedisTTLCache:
    def __init__(self, redis_url: str) -> None:
        import redis

        self._client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=1)

    def ping(self) -> None:
        self._client.ping()

    def set(self, key: str, value: Any, ttl_seconds: int = 120) -> None:
        import json

        self._client.setex(key, ttl_seconds, json.dumps(value, default=str))

    def get(self, key: str) -> Any | None:
        import json

        raw = self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)


class FallbackTTLCache:
    """Use Redis when available; otherwise fall back to in-process TTL cache."""

    def __init__(self, redis_url: str) -> None:
        self._fallback = LocalTTLCache()
        self._redis: RedisTTLCache | None = None

        try:
            redis_cache = RedisTTLCache(redis_url)
            redis_cache.ping()
            self._redis = redis_cache
        except Exception:
            self._redis = None

    def set(self, key: str, value: Any, ttl_seconds: int = 120) -> None:
        if self._redis is not None:
            try:
                self._redis.set(key, value, ttl_seconds=ttl_seconds)
                return
            except Exception:
                self._redis = None

        self._fallback.set(key, value, ttl_seconds=ttl_seconds)

    def get(self, key: str) -> Any | None:
        if self._redis is not None:
            try:
                return self._redis.get(key)
            except Exception:
                self._redis = None

        return self._fallback.get(key)


def build_cache(redis_url: str | None) -> LocalTTLCache | FallbackTTLCache:
    if not redis_url:
        return LocalTTLCache()

    return FallbackTTLCache(redis_url)
