"""Long-term memory storage interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class LongTermMemoryItem:
    content: str
    tags: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class LongTermMemory:
    """In-memory placeholder for durable memories."""

    def __init__(self) -> None:
        self._items: list[LongTermMemoryItem] = []

    def remember(self, content: str, tags: tuple[str, ...] = ()) -> LongTermMemoryItem:
        item = LongTermMemoryItem(content=content, tags=tags)
        self._items.append(item)
        return item

    def all(self) -> tuple[LongTermMemoryItem, ...]:
        return tuple(self._items)

