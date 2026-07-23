"""Text-to-speech abstraction."""

from __future__ import annotations

from voice.providers.base import SpeechProvider
from voice.voice_profile import VoiceProfile


class TextToSpeech:
    """Converts text into speech audio."""

    def synthesize(self, text: str) -> bytes:
        raise NotImplementedError("Text-to-speech is not implemented yet.")


class ProviderTextToSpeech:
    """Thin adapter around a replaceable speech provider."""

    def __init__(self, provider: SpeechProvider) -> None:
        self.provider = provider

    def speak(self, text: str, profile: VoiceProfile) -> str:
        return self.provider.speak(text, profile)
