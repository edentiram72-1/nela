"""Append-only in-memory audit log for permission decisions."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import json
import re
from types import MappingProxyType
from typing import Any
from uuid import uuid4

from permissions.models import PermissionDecision, PermissionTier


class AuditWriteError(RuntimeError):
    """Raised when the audit sink cannot persist an entry."""


SENSITIVE_KEYS = {
    "password",
    "passcode",
    "token",
    "secret",
    "private_key",
    "api_key",
    "authorization",
    "message_body",
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:ghp|github_pat|sk)-[A-Za-z0-9_\\-]{12,}"),
)


@dataclass(frozen=True)
class AuditRecord:
    """One permission or execution audit entry."""

    agent: str
    action: str
    tier: PermissionTier
    decision: PermissionDecision
    reason: str
    granted: bool
    capability: str | None = None
    session_id: str | None = None
    user_id: str | None = None
    target: str | None = None
    task_id: str | None = None
    plan_id: str | None = None
    command_id: str | None = None
    scope_session_id: str | None = None
    result_success: bool | None = None
    result_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    previous_hash: str | None = None
    entry_hash: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "target", redact(self.target) if self.target is not None else None)
        object.__setattr__(self, "result_message", redact(self.result_message) if self.result_message is not None else None)
        object.__setattr__(self, "metadata", MappingProxyType(redact(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.created_at.isoformat(),
            "event_id": self.id,
            "session_id": self.session_id,
            "user_identity_ref": self.user_id,
            "agent_id": self.agent,
            "capability": self.capability or self.action,
            "target": self.target,
            "permission_tier": self.tier.value,
            "policy_decision": self.decision.value,
            "authentication_result": self.metadata.get("authentication_result"),
            "confirmation_result": self.metadata.get("confirmation_result"),
            "execution_result": self.result_success,
            "error_code": self.metadata.get("error_code"),
            "rollback_result": self.metadata.get("rollback_result"),
            "previous_entry_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
            "granted": self.granted,
            "reason": self.reason,
            "task_id": self.task_id,
            "plan_id": self.plan_id,
            "command_id": self.command_id,
            "scope_session_id": self.scope_session_id,
            "result_message": self.result_message,
            "metadata": dict(self.metadata),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


class AuditLog:
    """Small append-only audit store.

    This is intentionally local and in-memory for Sprint 2. A durable writer can
    replace it later without changing the Permission Engine API.
    """

    def __init__(self, sink: Any | None = None) -> None:
        self._records: list[AuditRecord] = []
        self._sink = sink

    def append(self, record: AuditRecord) -> AuditRecord:
        previous_hash = self._records[-1].entry_hash if self._records else None
        chained = replace(record, previous_hash=previous_hash, entry_hash=None)
        chained = replace(chained, entry_hash=entry_hash(chained))
        if self._sink is not None:
            try:
                self._sink(chained.to_json())
            except Exception as error:
                raise AuditWriteError("Audit write failed.") from error
        self._records.append(chained)
        return chained

    def records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)

    def query(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        capability: str | None = None,
        agent: str | None = None,
        result: bool | None = None,
        session_id: str | None = None,
    ) -> tuple[AuditRecord, ...]:
        output = []
        for record in self._records:
            if start and record.created_at < start:
                continue
            if end and record.created_at > end:
                continue
            if capability and (record.capability or record.action) != capability:
                continue
            if agent and record.agent != agent:
                continue
            if result is not None and record.result_success is not result:
                continue
            if session_id and record.session_id != session_id and record.scope_session_id != session_id:
                continue
            output.append(record)
        return tuple(output)

    def clear(self) -> None:
        self._records.clear()

    def verify_chain(self) -> bool:
        previous_hash = None
        for record in self._records:
            if record.previous_hash != previous_hash:
                return False
            if record.entry_hash != entry_hash(replace(record, entry_hash=None)):
                return False
            previous_hash = record.entry_hash
        return True


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            normalized = str(key).lower()
            if any(sensitive in normalized for sensitive in SENSITIVE_KEYS):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact(item)
        return redacted
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        output = value
        for pattern in SECRET_PATTERNS:
            output = pattern.sub("[REDACTED]", output)
        return output
    return value


def entry_hash(record: AuditRecord) -> str:
    payload = record.to_dict()
    payload["entry_hash"] = None
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
