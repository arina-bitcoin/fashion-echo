from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class CacheItem:
    value: Any
    expires_at: datetime


class CacheService:
    """
    Простой in-memory кэш с TTL (по умолчанию 5 минут).
    Никакого Redis — всё в памяти процесса бэкенда.
    """

    def __init__(self, ttl_seconds: int = 300, max_items: int = 1000) -> None:
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_items = max_items
        self._store: Dict[str, CacheItem] = {}

    def _cleanup(self) -> None:
        """Удаляем протухшие записи и лишние при переполнении."""
        now = datetime.utcnow()
        # 1) убираем протухшие
        for key in list(self._store.keys()):
            item = self._store[key]
            if item.expires_at <= now:
                del self._store[key]

        # 2) если всё ещё слишком много — обрезаем по времени
        if len(self._store) > self.max_items:
            # сортировка по времени истечения, самые старые — первые
            ordered = sorted(
                self._store.items(),
                key=lambda kv: kv[1].expires_at,
            )
            for key, _ in ordered[: len(self._store) - self.max_items]:
                self._store.pop(key, None)

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        if item.expires_at <= datetime.utcnow():
            # протухло
            self._store.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: Any) -> None:
        self._cleanup()
        self._store[key] = CacheItem(
            value=value,
            expires_at=datetime.utcnow() + self.ttl,
        )

    def clear_prefix(self, prefix: str) -> None:
        """Удалить все ключи, начинающиеся с prefix."""
        for key in list(self._store.keys()):
            if key.startswith(prefix):
                self._store.pop(key, None)


cache = CacheService()
