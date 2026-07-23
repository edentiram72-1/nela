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
    speech_text: str | None = None
    min_stage: int = 1
    gender_tier: int = 1
    eye_state: str | None = None
    max_per_session: int = 2
    cooldown_group: str | None = None
    time_of_day: str | None = None
    humor: bool = False
    extra_fields: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PhraseEntry":
        known_fields = {
            "id",
            "text",
            "category",
            "language",
            "tone",
            "emotion",
            "formality",
            "gender",
            "weight",
            "requires",
            "tags",
            "enabled",
            "version",
            "speech_text",
            "min_stage",
            "gender_tier",
            "eye_state",
            "max_per_session",
            "cooldown_group",
            "time_of_day",
            "humor",
        }
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
            speech_text=str(data["speech_text"]) if data.get("speech_text") is not None else None,
            min_stage=int(data.get("min_stage", 1)),
            gender_tier=int(data.get("gender_tier", 1)),
            eye_state=str(data["eye_state"]) if data.get("eye_state") is not None else None,
            max_per_session=int(data.get("max_per_session", 2)),
            cooldown_group=str(data["cooldown_group"]) if data.get("cooldown_group") is not None else None,
            time_of_day=str(data["time_of_day"]) if data.get("time_of_day") is not None else None,
            humor=bool(data.get("humor", False)),
            extra_fields={str(key): value for key, value in data.items() if key not in known_fields},
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
    extra_fields: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersonalityProfile":
        known_fields = {
            "name",
            "preset",
            "language",
            "preferred_tones",
            "preferred_emotions",
            "formality",
            "gender",
            "style",
            "phrase_bias",
        }
        profile_name = str(data.get("name", data.get("preset", "default")))
        return cls(
            name=profile_name,
            language=str(data.get("language", "he")),
            preferred_tones=tuple(str(item) for item in data.get("preferred_tones", ("warm",))),
            preferred_emotions=tuple(str(item) for item in data.get("preferred_emotions", ("neutral",))),
            formality=str(data.get("formality", "casual")),
            gender=str(data.get("gender", "female")),
            style=str(data.get("style", profile_name)),
            phrase_bias={str(key): float(value) for key, value in data.get("phrase_bias", {}).items()},
            extra_fields={str(key): value for key, value in data.items() if key not in known_fields},
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
