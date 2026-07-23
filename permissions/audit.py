"""Append-only in-memory audit log for permission decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from permissions.models import PermissionDecision, PermissionTier


@dataclass(frozen=True)
class AuditRecord:
    """One permission or execution audit entry."""

    agent: str
    action: str
    tier: PermissionTier
    decision: PermissionDecision
    reason: str
    granted: bool
    user_id: str | None = None
    target: str | None = None
    task_id: str | None = None
    plan_id: str | None = None
    command_id: str | None = None
    scope_session_id: str | None = None
    result_success: bool | None = None
    result_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog:
    """Small append-only audit store.

    This is intentionally local and in-memory for Sprint 2. A durable writer can
    replace it later without changing the Permission Engine API.
    """

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def append(self, record: AuditRecord) -> AuditRecord:
        self._records.append(record)
        return record

    def records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)

    def clear(self) -> None:
        self._records.clear()
