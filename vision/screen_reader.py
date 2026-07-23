"""Screen reading abstraction."""

from __future__ import annotations

from vision.screen_capture import ScreenFrame


class ScreenReader:
    """Extracts readable text from a screen frame."""

    def read(self, frame: ScreenFrame) -> str:
        raise NotImplementedError("Screen reading is not implemented yet.")

