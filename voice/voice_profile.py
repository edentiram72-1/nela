"""Voice profile model for speech output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VoiceProfile:
    name: str = "nela_default"
    language: str = "he-IL"
    gender: str = "female"
    rate: float = 0.95
    pitch: float = 1.0
    volume: float = 1.0
    style: str = "warm_calm"
    provider_voice: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VoiceProfile":
        return cls(
            name=str(data.get("name", "nela_default")),
            language=str(data.get("language", "he-IL")),
            gender=str(data.get("gender", "female")),
            rate=float(data.get("rate", 0.95)),
            pitch=float(data.get("pitch", 1.0)),
            volume=float(data.get("volume", 1.0)),
            style=str(data.get("style", "warm_calm")),
            provider_voice=str(data["provider_voice"]) if data.get("provider_voice") else None,
        )
