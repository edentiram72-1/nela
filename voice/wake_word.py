"""Wake word detection abstraction."""

from __future__ import annotations

from voice.microphone import AudioFrame


class WakeWordDetector:
    """Detects whether the assistant should start listening."""

    def is_wake_word(self, audio: AudioFrame) -> bool:
        raise NotImplementedError("Wake word detection is not implemented yet.")

