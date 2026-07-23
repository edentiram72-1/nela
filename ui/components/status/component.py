"""Status bar component."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.state import UIState
from ui.theme import Theme


class StatusComponent:
    """Displays Brain status, Agent activity, and notifications."""

    def __init__(self, parent: tk.Misc) -> None:
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, anchor=tk.W)
        self.label.pack(fill=tk.X, padx=8, pady=4)

    def render(self, state: UIState, theme: Theme) -> None:
        latest_activity = state.agent_activity[-1].status if state.agent_activity else "none"
        latest_notification = state.notifications[-1].message if state.notifications else "none"
        self.label.configure(
            text=(
                f"Brain: {state.brain_status} | "
                f"Eye: {state.eye_state.value} | "
                f"Agent: {latest_activity} | "
                f"Notification: {latest_notification}"
            ),
            foreground=theme.muted_text,
            background=theme.surface,
            font=(theme.font_family, theme.font_size),
        )
