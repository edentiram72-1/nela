"""Session memory storage."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class SessionMemoryItem:
    user_text: str
    intent: str
    created_at: datetime


class ShortTermMemory:
    """Stores conversation context for the current session."""

    def __init__(self) -> None:
        self._items: list[SessionMemoryItem] = []

    def add_turn(self, user_text: str, intent: str) -> None:
        self._items.append(
            SessionMemoryItem(
                user_text=user_text,
                intent=intent,
                created_at=datetime.now(timezone.utc),
            )
        )

    def recent(self, limit: int = 10) -> tuple[SessionMemoryItem, ...]:
        return tuple(self._items[-limit:])

