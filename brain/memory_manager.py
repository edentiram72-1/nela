"""Brain-level memory orchestration."""

from __future__ import annotations

from brain.intent_router import Intent
from core.events import Event, EventBus, EventTypes
from memory.long_term import LongTermMemory, LongTermMemoryItem
from memory.short_term import ShortTermMemory


class MemoryManager:
    """Coordinates short-term and long-term memory updates."""

    def __init__(
        self,
        short_term: ShortTermMemory,
        long_term: LongTermMemory,
        events: EventBus,
    ) -> None:
        self.short_term = short_term
        self.long_term = long_term
        self.events = events

    def record_turn(self, user_text: str, intent: Intent) -> None:
        self.short_term.add_turn(user_text, intent.action)
        self.events.publish(
            Event(
                type=EventTypes.MEMORY_UPDATED,
                source="brain.memory_manager",
                payload={"layer": "short_term", "intent": intent.action},
            )
        )

    def remember(self, content: str, tags: tuple[str, ...] = ()) -> LongTermMemoryItem:
        item = self.long_term.remember(content, tags)
        self.events.publish(
            Event(
                type=EventTypes.MEMORY_UPDATED,
                source="brain.memory_manager",
                payload={"layer": "long_term", "memory_id": item.id, "tags": tags},
            )
        )
        return item

    def recent_context(self, limit: int = 10) -> tuple[object, ...]:
        self.events.publish(
            Event(
                type=EventTypes.MEMORY_RETRIEVED,
                source="brain.memory_manager",
                payload={"layer": "short_term", "limit": limit},
            )
        )
        return self.short_term.recent(limit)

