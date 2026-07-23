"""Text-to-speech abstraction."""

from __future__ import annotations


class TextToSpeech:
    """Converts text into speech audio."""

    def synthesize(self, text: str) -> bytes:
        raise NotImplementedError("Text-to-speech is not implemented yet.")

