"""Runtime language selection context."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque


@dataclass
class LanguageRuntimeContext:
    """Tracks recent phrase usage and current voice/personality preferences."""

    language: str = "he"
    gender: str = "unknown"
    relationship_stage: int = 1
    recent_phrase_ids: Deque[str] = field(default_factory=lambda: deque(maxlen=20))
    phrase_use_counts: dict[str, int] = field(default_factory=dict)

    def remember_phrase(self, phrase_id: str) -> None:
        self.recent_phrase_ids.append(phrase_id)
        self.phrase_use_counts[phrase_id] = self.phrase_use_counts.get(phrase_id, 0) + 1

    def was_recent(self, phrase_id: str) -> bool:
        return phrase_id in self.recent_phrase_ids

    def use_count(self, phrase_id: str) -> int:
        return self.phrase_use_counts.get(phrase_id, 0)
