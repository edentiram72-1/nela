"""Desktop agent placeholder."""

from __future__ import annotations

from agents.mock import MockAgent


class DesktopAgent(MockAgent):
    name = "desktop"
    capability = "desktop_control"
