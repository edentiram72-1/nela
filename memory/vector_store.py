"""Vector store abstraction placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VectorRecord:
    id: str
    text: str
    embedding: tuple[float, ...]
    metadata: dict[str, str]


class VectorStore:
    """Minimal in-memory vector store placeholder."""

    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    def upsert(self, record: VectorRecord) -> None:
        self._records[record.id] = record

    def get(self, record_id: str) -> VectorRecord | None:
        return self._records.get(record_id)

