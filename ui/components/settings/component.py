"""Settings component placeholder for future Claude UI."""

from __future__ import annotations

from ui.theme import ThemeManager, ThemeName


class SettingsController:
    """Non-visual settings controller for theme switching."""

    def __init__(self, theme_manager: ThemeManager) -> None:
        self.theme_manager = theme_manager

    def switch_theme(self, theme: ThemeName | str) -> None:
        self.theme_manager.switch(theme)
