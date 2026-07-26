"""Persistent learning memory for NELA study sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LearningLesson:
    """One structured lesson NELA learned from an authorized study source."""

    id: str
    source: str
    topic: str
    summary: str
    concepts: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()
    safety_notes: tuple[str, ...] = ()
    room: str | None = None
    tags: tuple[str, ...] = ()
    created_at: str = ""

    @classmethod
    def create(
        cls,
        source: str,
        topic: str,
        summary: str,
        concepts: tuple[str, ...] = (),
        commands: tuple[str, ...] = (),
        safety_notes: tuple[str, ...] = (),
        room: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> "LearningLesson":
        created_at = datetime.now(timezone.utc).isoformat()
        identity = hashlib.sha256(
            "\n".join((source, topic, summary, room or "", created_at)).encode("utf-8")
        ).hexdigest()[:16]
        return cls(
            id=f"lesson.{identity}",
            source=source,
            topic=topic,
            summary=summary,
            concepts=concepts,
            commands=commands,
            safety_notes=safety_notes,
            room=room,
            tags=tags,
            created_at=created_at,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearningLesson":
        return cls(
            id=str(data["id"]),
            source=str(data.get("source", "unknown")),
            topic=str(data.get("topic", "general")),
            summary=str(data.get("summary", "")),
            concepts=tuple(str(item) for item in data.get("concepts", ())),
            commands=tuple(str(item) for item in data.get("commands", ())),
            safety_notes=tuple(str(item) for item in data.get("safety_notes", ())),
            room=str(data["room"]) if data.get("room") else None,
            tags=tuple(str(item) for item in data.get("tags", ())),
            created_at=str(data.get("created_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "topic": self.topic,
            "summary": self.summary,
            "concepts": list(self.concepts),
            "commands": list(self.commands),
            "safety_notes": list(self.safety_notes),
            "room": self.room,
            "tags": list(self.tags),
            "created_at": self.created_at,
        }


class LearningMemoryStore:
    """Small JSON-backed store for study lessons and skill graph signals."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._lessons: dict[str, LearningLesson] = {}
        if self.path is not None:
            self._load()

    def add_lesson(
        self,
        source: str,
        topic: str,
        summary: str,
        concepts: tuple[str, ...] = (),
        commands: tuple[str, ...] = (),
        safety_notes: tuple[str, ...] = (),
        room: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> LearningLesson:
        if not topic.strip():
            raise ValueError("Learning topic cannot be empty.")
        if not summary.strip():
            raise ValueError("Lesson summary cannot be empty.")
        lesson = LearningLesson.create(
            source=source.strip() or "unknown",
            topic=topic.strip(),
            summary=summary.strip(),
            concepts=_unique(concepts),
            commands=_unique(commands),
            safety_notes=_unique(safety_notes),
            room=room.strip() if room and room.strip() else None,
            tags=_unique(tags),
        )
        self._lessons[lesson.id] = lesson
        self._save()
        return lesson

    def list_lessons(self, source: str | None = None) -> tuple[LearningLesson, ...]:
        lessons = tuple(sorted(self._lessons.values(), key=lambda item: item.created_at))
        if source is None:
            return lessons
        normalized = source.strip().lower()
        return tuple(item for item in lessons if item.source.lower() == normalized)

    def skill_graph(self, source: str | None = None) -> dict[str, int]:
        graph: dict[str, int] = {}
        for lesson in self.list_lessons(source=source):
            for concept in (*lesson.concepts, *lesson.tags):
                key = concept.strip().lower()
                if not key:
                    continue
                graph[key] = graph.get(key, 0) + 1
        return dict(sorted(graph.items(), key=lambda item: (-item[1], item[0])))

    def _load(self) -> None:
        if self.path is None or not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        lessons = data.get("lessons", ()) if isinstance(data, dict) else ()
        self._lessons = {
            lesson.id: lesson
            for lesson in (LearningLesson.from_dict(item) for item in lessons if isinstance(item, dict))
        }

    def _save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "lessons": [lesson.to_dict() for lesson in self.list_lessons()]}
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp_path.replace(self.path)


def _unique(values: tuple[str, ...]) -> tuple[str, ...]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = " ".join(str(value).strip().split())
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        output.append(cleaned)
        seen.add(key)
    return tuple(output)
