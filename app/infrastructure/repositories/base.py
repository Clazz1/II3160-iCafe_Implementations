from __future__ import annotations

from abc import ABC
from typing import Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class AbstractInMemoryRepository(ABC, Generic[T]):
    def __init__(self) -> None:
        self._items: Dict[str, T] = {}

    def add(self, entity: T) -> None:
        entity_id = getattr(entity, "id")
        self._items[entity_id] = entity

    def get(self, entity_id: str) -> Optional[T]:
        return self._items.get(entity_id)

    def list(self) -> List[T]:
        return list(self._items.values())

    def update(self, entity: T) -> None:
        entity_id = getattr(entity, "id")
        if entity_id not in self._items:
            raise KeyError("Entity not found")
        self._items[entity_id] = entity
