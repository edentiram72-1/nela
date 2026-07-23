"""Theme tokens for Claude-provided visual design."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ThemeName(str, Enum):
    DARK = "dark"
    LIGHT = "light"
    PSYCHEDELIC = "psychedelic"


@dataclass(frozen=True)
class Theme:
    name: ThemeName
    background: str
    surface: str
    text: str
    muted_text: str
    accent: str
    success: str
    warning: str
    error: str
    border: str
    font_family: str
    font_size: int
    spacing_unit: int


THEMES: dict[ThemeName, Theme] = {
    ThemeName.DARK: Theme(
        name=ThemeName.DARK,
        background="#080514",
        surface="#120B26",
        text="#EDE8FF",
        muted_text="#8D84B8",
        accent="#37B8A8",
        success="#39D97A",
        warning="#FFB020",
        error="#FF4D5E",
        border="rgba(160,140,255,.14)",
        font_family="Assistant",
        font_size=15,
        spacing_unit=8,
    ),
    ThemeName.LIGHT: Theme(
        name=ThemeName.LIGHT,
        background="#F7F4FF",
        surface="#FFFFFF",
        text="#171127",
        muted_text="#6B5F8F",
        accent="#37B8A8",
        success="#168A50",
        warning="#9E6410",
        error="#B83245",
        border="rgba(90,70,150,.18)",
        font_family="Assistant",
        font_size=15,
        spacing_unit=8,
    ),
    ThemeName.PSYCHEDELIC: Theme(
        name=ThemeName.PSYCHEDELIC,
        background="#080514",
        surface="#120B26",
        text="#EDE8FF",
        muted_text="#8D84B8",
        accent="#C86BFF",
        success="#39D97A",
        warning="#FFB020",
        error="#FF4D5E",
        border="rgba(160,140,255,.14)",
        font_family="Assistant",
        font_size=15,
        spacing_unit=8,
    ),
}


class ThemeManager:
    """Provides active theme tokens without hardcoding colors in components."""

    def __init__(self, active: ThemeName = ThemeName.DARK) -> None:
        self._active = active

    @property
    def active_name(self) -> ThemeName:
        return self._active

    @property
    def active(self) -> Theme:
        return THEMES[self._active]

    def switch(self, name: ThemeName | str) -> Theme:
        theme_name = name if isinstance(name, ThemeName) else ThemeName(str(name))
        self._active = theme_name
        return self.active
