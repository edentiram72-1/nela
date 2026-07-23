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
        background="#101114",
        surface="#181a1f",
        text="#f2f4f8",
        muted_text="#a7adbb",
        accent="#5fb3ff",
        success="#5fd19a",
        warning="#f2c94c",
        error="#ff6b6b",
        border="#2a2f3a",
        font_family="Helvetica",
        font_size=13,
        spacing_unit=8,
    ),
    ThemeName.LIGHT: Theme(
        name=ThemeName.LIGHT,
        background="#f7f8fb",
        surface="#ffffff",
        text="#14171f",
        muted_text="#596174",
        accent="#2563eb",
        success="#16855a",
        warning="#9a6700",
        error="#c73535",
        border="#d9deea",
        font_family="Helvetica",
        font_size=13,
        spacing_unit=8,
    ),
    ThemeName.PSYCHEDELIC: Theme(
        name=ThemeName.PSYCHEDELIC,
        background="#120f24",
        surface="#1e1938",
        text="#faf7ff",
        muted_text="#c8bfe2",
        accent="#00d4ff",
        success="#00f59b",
        warning="#ffcf40",
        error="#ff4f9a",
        border="#4f3d7a",
        font_family="Helvetica",
        font_size=13,
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
