"""Persistent learned-response storage for local NELA language learning."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any


@dataclass(frozen=True)
class LearnedResponse:
    """One user-taught trigger and response pair."""

    id: str
    trigger: str
    response: str
    normalized_trigger: str
    tags: tuple[str, ...] = ()
    source: str = "user"
    created_at: str = ""

    @classmethod
    def create(cls, trigger: str, response: str, tags: tuple[str, ...] = (), source: str = "user") -> "LearnedResponse":
        normalized = normalize_trigger(trigger)
        created_at = datetime.now(timezone.utc).isoformat()
        identity = hashlib.sha256(f"{normalized}\n{response.strip()}".encode("utf-8")).hexdigest()[:16]
        return cls(
            id=f"learned.{identity}",
            trigger=trigger.strip(),
            response=response.strip(),
            normalized_trigger=normalized,
            tags=tags,
            source=source,
            created_at=created_at,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnedResponse":
        return cls(
            id=str(data["id"]),
            trigger=str(data["trigger"]),
            response=str(data["response"]),
            normalized_trigger=str(data.get("normalized_trigger") or normalize_trigger(str(data["trigger"]))),
            tags=tuple(str(item) for item in data.get("tags", ())),
            source=str(data.get("source", "user")),
            created_at=str(data.get("created_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "trigger": self.trigger,
            "response": self.response,
            "normalized_trigger": self.normalized_trigger,
            "tags": list(self.tags),
            "source": self.source,
            "created_at": self.created_at,
        }


class LearnedResponseStore:
    """Small append/update store for user-taught response pairs."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._responses: dict[str, LearnedResponse] = {}
        if self.path is not None:
            self._load()

    def add_response(
        self,
        trigger: str,
        response: str,
        tags: tuple[str, ...] = (),
        source: str = "user",
    ) -> LearnedResponse:
        if not trigger.strip():
            raise ValueError("Trigger cannot be empty.")
        if not response.strip():
            raise ValueError("Response cannot be empty.")
        learned = LearnedResponse.create(trigger=trigger, response=response, tags=tags, source=source)
        self._responses[learned.normalized_trigger] = learned
        self._save()
        return learned

    def find_response(self, text: str) -> LearnedResponse | None:
        normalized = normalize_trigger(text)
        if normalized in self._responses:
            return self._responses[normalized]
        for learned in self._responses.values():
            if learned.normalized_trigger and learned.normalized_trigger in normalized:
                return learned
        return None

    def list_responses(self) -> tuple[LearnedResponse, ...]:
        return tuple(sorted(self._responses.values(), key=lambda item: item.created_at))

    def _load(self) -> None:
        if self.path is None or not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        responses = data.get("responses", ()) if isinstance(data, dict) else ()
        self._responses = {
            learned.normalized_trigger: learned
            for learned in (LearnedResponse.from_dict(item) for item in responses if isinstance(item, dict))
        }

    def _save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "responses": [item.to_dict() for item in self.list_responses()]}
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp_path.replace(self.path)


def normalize_trigger(text: str) -> str:
    cleaned = re.sub(r"^[\s,.:;!?\"'׳״]+|[\s,.:;!?\"'׳״]+$", "", text.lower())
    cleaned = re.sub(r"^(?:נלה|nela)[,\s]+", "", cleaned)
    return " ".join(cleaned.split())
