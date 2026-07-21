"""Speech-to-text abstraction."""

from __future__ import annotations

from voice.microphone import AudioFrame


class SpeechToText:
    """Transcribes audio into text."""

    def transcribe(self, audio: AudioFrame) -> str:
        raise NotImplementedError("Speech-to-text is not implemented yet.")

