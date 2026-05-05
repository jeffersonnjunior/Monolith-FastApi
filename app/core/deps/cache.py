from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class IdempotencyCacheEntry:
    status: str
    payload: dict[str, Any]


class IdempotencyCache:
    def __init__(self) -> None:
        self._entries: MutableMapping[str, IdempotencyCacheEntry] = {}

    async def get(self, key: str) -> IdempotencyCacheEntry | None:
        return self._entries.get(key)

    async def set(self, key: str, entry: IdempotencyCacheEntry) -> None:
        self._entries[key] = entry


_cache = IdempotencyCache()


def get_idempotency_cache() -> IdempotencyCache:
    return _cache
