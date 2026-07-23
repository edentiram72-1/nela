"""Sidebar shell for navigation placeholders."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.state import UIState
from ui.theme import Theme


class SidebarComponent:
    """Hosts future navigation and workspace controls."""

    def __init__(self, parent: tk.Misc) -> None:
        self.frame = ttk.Frame(parent, width=180)
        self.label = ttk.Label(self.frame, anchor=tk.NW, justify=tk.LEFT)
        self.label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def render(self, state: UIState, theme: Theme) -> None:
        self.label.configure(
            text="NELA OS\n\nChat\nAgents\nMemory\nSettings",
            foreground=theme.text,
            background=theme.surface,
            font=(theme.font_family, theme.font_size),
        )
