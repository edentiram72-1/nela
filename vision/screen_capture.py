"""Screen capture abstraction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScreenFrame:
    width: int
    height: int
    pixels: bytes


class ScreenCapture:
    """Captures the current screen."""

    def capture(self) -> ScreenFrame:
        raise NotImplementedError("Screen capture is not implemented yet.")

