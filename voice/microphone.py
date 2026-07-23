"""Microphone input abstraction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioFrame:
    data: bytes
    sample_rate: int


class Microphone:
    """Placeholder microphone adapter."""

    def listen(self) -> AudioFrame:
        raise NotImplementedError("Microphone capture is not implemented yet.")

