"""Voice status component."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.state import UIState
from ui.theme import Theme


class VoiceComponent:
    """Displays voice input/output readiness without implementing audio yet."""

    def __init__(self, parent: tk.Misc) -> None:
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, anchor=tk.W)
        self.label.pack(fill=tk.X, padx=8, pady=(0, 8))

    def render(self, state: UIState, theme: Theme) -> None:
        input_status = "on" if state.voice_input_active else "off"
        output_status = "on" if state.voice_output_active else "off"
        self.label.configure(
            text=f"Voice input: {input_status} | Voice output: {output_status}",
            foreground=theme.muted_text,
            background=theme.background,
            font=(theme.font_family, theme.font_size),
        )
