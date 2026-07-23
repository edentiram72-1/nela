"""UI element detection abstraction."""

from __future__ import annotations

from dataclasses import dataclass

from vision.screen_capture import ScreenFrame


@dataclass(frozen=True)
class UIElement:
    label: str
    role: str
    bounds: tuple[int, int, int, int]


class UIDetector:
    """Detects buttons, inputs, and other UI elements."""

    def detect(self, frame: ScreenFrame) -> tuple[UIElement, ...]:
        raise NotImplementedError("UI detection is not implemented yet.")

