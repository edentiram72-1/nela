"""Data models for language packs and personality profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PhraseEntry:
    id: str
    text: str
    category: str
    language: str
    tone: tuple[str, ...] = ()
    emotion: str = "neutral"
    formality: str = "casual"
    gender: str = "female"
    weight: float = 1.0
    requires: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    enabled: bool = True
    version: str = "1.0"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PhraseEntry":
        return cls(
            id=str(data["id"]),
            text=str(data["text"]),
            category=str(data["category"]),
            language=str(data["language"]),
            tone=tuple(str(item) for item in data.get("tone", ())),
            emotion=str(data.get("emotion", "neutral")),
            formality=str(data.get("formality", "casual")),
            gender=str(data.get("gender", "female")),
            weight=float(data.get("weight", 1.0)),
            requires=tuple(str(item) for item in data.get("requires", ())),
            tags=tuple(str(item) for item in data.get("tags", ())),
            enabled=bool(data.get("enabled", True)),
            version=str(data.get("version", "1.0")),
        )


@dataclass(frozen=True)
class LanguagePack:
    language: str
    version: str
    categories: tuple[str, ...]
    tones: tuple[str, ...]
    emotions: tuple[str, ...]
    entries: tuple[PhraseEntry, ...]
    source: str

    def enabled_entries(self) -> tuple[PhraseEntry, ...]:
        return tuple(entry for entry in self.entries if entry.enabled)


@dataclass(frozen=True)
class PersonalityProfile:
    name: str
    language: str = "he"
    preferred_tones: tuple[str, ...] = ("warm",)
    preferred_emotions: tuple[str, ...] = ("neutral",)
    formality: str = "casual"
    gender: str = "female"
    style: str = "default"
    phrase_bias: dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersonalityProfile":
        return cls(
            name=str(data["name"]),
            language=str(data.get("language", "he")),
            preferred_tones=tuple(str(item) for item in data.get("preferred_tones", ("warm",))),
            preferred_emotions=tuple(str(item) for item in data.get("preferred_emotions", ("neutral",))),
            formality=str(data.get("formality", "casual")),
            gender=str(data.get("gender", "female")),
            style=str(data.get("style", data["name"])),
            phrase_bias={str(key): float(value) for key, value in data.get("phrase_bias", {}).items()},
        )


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    entry_id: str | None = None
    file: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.issues
