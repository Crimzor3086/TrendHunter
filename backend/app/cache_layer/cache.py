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


cache = LocalTTLCache()
