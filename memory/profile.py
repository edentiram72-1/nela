"""User profile memory."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UserProfile:
    name: str | None = None
    preferences: dict[str, str] = field(default_factory=dict)
    projects: list[str] = field(default_factory=list)

    def set_preference(self, key: str, value: str) -> None:
        self.preferences[key] = value

