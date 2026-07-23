"""Intent recognition for NELA OS."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Priority(str, Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


@dataclass(frozen=True)
class Intent:
    """Structured representation of a user request."""

    action: str
    raw_text: str
    confidence: float
    application: str | None = None
    resource: str | None = None
    priority: Priority = Priority.NORMAL
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False

    @property
    def name(self) -> str:
        return self.action

    @property
    def target_agent(self) -> str | None:
        if self.application:
            return _slug(self.application)
        if self.parameters.get("domain"):
            return str(self.parameters["domain"])
        return None


@dataclass(frozen=True)
class IntentPattern:
    """Configurable pattern for turning text into an intent."""

    action: str
    keywords: tuple[str, ...]
    domain: str | None = None
    requires_confirmation: bool = False


DEFAULT_PATTERNS: tuple[IntentPattern, ...] = (
    IntentPattern("Remember", ("remember", "save this", "learn this")),
    IntentPattern("StopTask", ("stop", "cancel"), requires_confirmation=True),
    IntentPattern("PlayMedia", ("play", "music", "playlist", "song")),
    IntentPattern("OpenApplication", ("open", "launch", "start")),
    IntentPattern("Search", ("search", "find", "look up")),
    IntentPattern("CreateItem", ("create", "make", "draft", "write")),
)


class IntentRouter:
    """Converts text into structured, agent-neutral intents."""

    def __init__(self, patterns: tuple[IntentPattern, ...] = DEFAULT_PATTERNS) -> None:
        self._patterns = patterns

    def classify(self, text: str, context: dict[str, Any] | None = None) -> Intent:
        normalized = _normalize(text)
        priority = _detect_priority(normalized)
        pattern = self._match_pattern(normalized)
        application = _extract_application(text)
        resource = _extract_resource(text)
        parameters: dict[str, Any] = {}
        if pattern and pattern.domain:
            parameters["domain"] = pattern.domain
        if _looks_like_follow_up(normalized) and context:
            parameters["follow_up_to"] = context.get("last_intent")

        if pattern:
            return Intent(
                action=pattern.action,
                raw_text=text,
                confidence=0.82,
                application=application,
                resource=resource,
                priority=priority,
                parameters=parameters,
                requires_confirmation=pattern.requires_confirmation,
            )

        return Intent(
            action="GeneralRequest",
            raw_text=text,
            confidence=0.45,
            application=application,
            resource=resource,
            priority=priority,
            parameters=parameters,
        )

    def _match_pattern(self, normalized: str) -> IntentPattern | None:
        for pattern in self._patterns:
            if any(_contains_keyword(normalized, keyword) for keyword in pattern.keywords):
                return pattern
        return None


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _detect_priority(normalized: str) -> Priority:
    if any(word in normalized for word in ("urgent", "immediately", "asap", "now")):
        return Priority.HIGH
    if any(word in normalized for word in ("later", "when you can")):
        return Priority.LOW
    return Priority.NORMAL


def _extract_application(text: str) -> str | None:
    match = re.search(
        r"\b(?:open|launch|start)\s+([A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return _title_name(_trim_application_name(match.group(1).strip()))
    match = re.search(
        r"\bin\s+([A-Z][\w-]*(?:\s+[A-Z][\w-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return _title_name(_trim_application_name(match.group(1).strip()))
    return None


def _extract_resource(text: str) -> str | None:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return quoted.group(1).strip()
    playlist = re.search(r"\bmy\s+([\w\s-]+?)\s+playlist\b", text, flags=re.IGNORECASE)
    if playlist:
        return playlist.group(1).strip()
    return None


def _looks_like_follow_up(normalized: str) -> bool:
    return normalized.startswith(("also ", "then ", "and ", "do that", "same "))


def _contains_keyword(normalized: str, keyword: str) -> bool:
    escaped = re.escape(_normalize(keyword))
    return re.search(rf"(?<!\w){escaped}(?!\w)", normalized) is not None


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _title_name(value: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in value.split())


def _trim_application_name(value: str) -> str:
    stopwords = {"and", "then", "to", "with", "for", "play", "search", "open"}
    parts = []
    for part in value.split():
        if part.lower() in stopwords:
            break
        parts.append(part)
    return " ".join(parts) if parts else value
