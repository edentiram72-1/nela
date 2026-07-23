"""Tkinter desktop window for the NELA UI foundation."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.startup import NelaRuntime
from ui.components.chat.component import ChatComponent
from ui.components.eye.component import EyeComponent
from ui.components.sidebar.component import SidebarComponent
from ui.components.status.component import StatusComponent
from ui.components.voice.component import VoiceComponent
from ui.events import UIEventBridge
from ui.router import UIRouter
from ui.state import UIState, UIStateManager
from ui.theme import ThemeManager


class NelaWindow:
    """Desktop shell that hosts Claude's future UI assets."""

    def __init__(
        self,
        runtime: NelaRuntime,
        state: UIStateManager | None = None,
        theme: ThemeManager | None = None,
    ) -> None:
        self.runtime = runtime
        self.state = state or UIStateManager()
        self.theme = theme or ThemeManager()
        self.router = UIRouter(runtime=runtime, state=self.state)
        self.root = tk.Tk()
        self.bridge = UIEventBridge(runtime.events, self.state, schedule_idle=self.root.after)
        self.root.title("NELA OS")
        self.root.minsize(900, 620)
        self._build()
        self.bridge.start()
        self.state.subscribe(self.render)

    def run(self) -> None:
        self.root.mainloop()

    def render(self, state: UIState) -> None:
        theme = self.theme.active
        self.root.configure(bg=theme.background)
        self.sidebar.render(state, theme)
        self.eye.render(state, theme)
        self.chat.render(state, theme)
        self.status.render(state, theme)
        self.voice.render(state, theme)

    def _build(self) -> None:
        theme = self.theme.active
        self.root.configure(bg=theme.background)
        self.shell = ttk.Frame(self.root)
        self.shell.pack(fill=tk.BOTH, expand=True)

        self.sidebar = SidebarComponent(self.shell)
        self.sidebar.frame.pack(side=tk.LEFT, fill=tk.Y)

        self.main = ttk.Frame(self.shell)
        self.main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.eye = EyeComponent(self.main)
        self.eye.frame.pack(fill=tk.X)

        self.chat = ChatComponent(self.main, on_submit=self.router.submit_text)
        self.chat.frame.pack(fill=tk.BOTH, expand=True)

        self.status = StatusComponent(self.main)
        self.status.frame.pack(fill=tk.X)

        self.voice = VoiceComponent(self.main)
        self.voice.frame.pack(fill=tk.X)
