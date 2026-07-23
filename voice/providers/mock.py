"""Mock speech provider for tests and silent development workflows."""

from __future__ import annotations

from uuid import uuid4

from voice.providers.base import SpeechProvider
from voice.voice_profile import VoiceProfile


class MockSpeechProvider(SpeechProvider):
    """Deterministic provider that records speech requests without audio output."""

    name = "mock"

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.spoken: list[tuple[str, VoiceProfile]] = []
        self.stopped = False
        self.paused = False

    def speak(self, text: str, profile: VoiceProfile) -> str:
        if self.fail:
            raise RuntimeError("Mock provider failure.")
        self.spoken.append((text, profile))
        self.stopped = False
        return str(uuid4())

    def stop(self) -> None:
        self.stopped = True

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def health_check(self) -> dict[str, object]:
        return {
            "provider": self.name,
            "available": not self.fail,
            "supports_pause": True,
            "supports_resume": True,
            "spoken_count": len(self.spoken),
        }
