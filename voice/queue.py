"""Speech queue primitives."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque
from uuid import uuid4

from voice.voice_profile import VoiceProfile


@dataclass(frozen=True)
class SpeechRequest:
    text: str
    profile: VoiceProfile
    interrupt: bool = False
    silent: bool | None = None
    id: str = field(default_factory=lambda: str(uuid4()))


class SpeechQueue:
    """Small FIFO queue for speech requests."""

    def __init__(self) -> None:
        self._items: Deque[SpeechRequest] = deque()

    def enqueue(self, request: SpeechRequest) -> None:
        if request.interrupt:
            self.clear()
        self._items.append(request)

    def next(self) -> SpeechRequest | None:
        if not self._items:
            return None
        return self._items.popleft()

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
