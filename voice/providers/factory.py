"""Speech provider selection."""

from __future__ import annotations

from voice.providers.base import SpeechProvider
from voice.providers.macos import MacOSSpeechProvider
from voice.providers.mock import MockSpeechProvider


def create_speech_provider(name: str) -> SpeechProvider:
    normalized = name.strip().lower()
    if normalized in {"macos", "macos_say", "say"}:
        return MacOSSpeechProvider()
    if normalized in {"mock", "test"}:
        return MockSpeechProvider()
    raise ValueError(f"Unsupported speech provider: {name}")
