"""Chat component with Markdown-friendly text rendering."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from brain.conversation import ConversationTurn
from ui.state import MessageRole, UIState
from ui.theme import Theme

SubmitHandler = Callable[[str], ConversationTurn]


class ChatComponent:
    """Displays conversation history and accepts text input."""

    def __init__(self, parent: tk.Misc, on_submit: SubmitHandler) -> None:
        self.on_submit = on_submit
        self.frame = ttk.Frame(parent)
        self.history = tk.Text(self.frame, wrap=tk.WORD, height=24)
        self.history.configure(state=tk.DISABLED)
        self.history.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.input = ttk.Entry(self.frame)
        self.input.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.input.bind("<Return>", self._submit)

    def render(self, state: UIState, theme: Theme) -> None:
        self.history.configure(
            background=theme.surface,
            foreground=theme.text,
            insertbackground=theme.text,
            font=(theme.font_family, theme.font_size),
        )
        self.history.configure(state=tk.NORMAL)
        self.history.delete("1.0", tk.END)
        for message in state.messages:
            label = _label_for_role(message.role)
            streaming = " ..." if message.streaming else ""
            self.history.insert(tk.END, f"{label}{streaming}\n{message.content}\n\n")
        if state.typing_indicator:
            self.history.insert(tk.END, "NELA is typing...\n")
        self.history.configure(state=tk.DISABLED)
        self.history.see(tk.END)

    def _submit(self, event: object) -> None:
        text = self.input.get().strip()
        if not text:
            return
        self.input.delete(0, tk.END)
        self.on_submit(text)


def _label_for_role(role: MessageRole) -> str:
    if role == MessageRole.USER:
        return "User"
    if role == MessageRole.ASSISTANT:
        return "NELA"
    return "System"
