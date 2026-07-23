"""Runtime language selection context."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque


@dataclass
class LanguageRuntimeContext:
    """Tracks recent phrase usage and current voice/personality preferences."""

    language: str = "he"
    gender: str = "female"
    recent_phrase_ids: Deque[str] = field(default_factory=lambda: deque(maxlen=20))

    def remember_phrase(self, phrase_id: str) -> None:
        self.recent_phrase_ids.append(phrase_id)

    def was_recent(self, phrase_id: str) -> bool:
        return phrase_id in self.recent_phrase_ids
