"""Provider contract for speech synthesis backends."""

from __future__ import annotations

from abc import ABC, abstractmethod

from voice.voice_profile import VoiceProfile


class SpeechProvider(ABC):
    """Replaceable text-to-speech provider."""

    name: str

    @abstractmethod
    def speak(self, text: str, profile: VoiceProfile) -> str:
        """Speak text and return provider-specific utterance id."""

    @abstractmethod
    def stop(self) -> None:
        """Stop current speech."""

    def pause(self) -> None:
        """Pause speech when supported."""

    def resume(self) -> None:
        """Resume speech when supported."""

    @abstractmethod
    def health_check(self) -> dict[str, object]:
        """Return provider health metadata."""
