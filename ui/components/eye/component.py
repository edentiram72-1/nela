"""State-only NELA Eye placeholder component."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.state import UIState
from ui.theme import Theme


class EyeComponent:
    """Exposes Eye states for future Claude SVG and animation assets."""

    def __init__(self, parent: tk.Misc) -> None:
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, anchor=tk.CENTER)
        self.label.pack(fill=tk.X, padx=8, pady=8)

    def render(self, state: UIState, theme: Theme) -> None:
        self.label.configure(
            text=f"Eye: {state.eye_state.value}",
            foreground=theme.accent,
            background=theme.background,
            font=(theme.font_family, theme.font_size + 2),
        )
