"""Data models for local authorized cyber-lab actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class AuthorizationScopeType(str, Enum):
    LOCAL_LAB = "local_lab"
    CTF = "ctf"
    OWNED_ASSET = "owned_asset"
    WORKSPACE_ARTIFACT = "workspace_artifact"


class CyberLabDecisionType(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    APPROVAL_REQUIRED = "approval_required"
    KILL_SWITCH_ACTIVE = "kill_switch_active"
    DRY_RUN_ONLY = "dry_run_only"


FORBIDDEN_ACTIONS: frozenset[str] = frozenset(
    {
        "external_targeting",
        "persistence",
        "credential_theft",
        "malware_deployment",
        "evasion",
        "exfiltration",
    }
)


@dataclass(frozen=True)
class CyberLabTarget:
    identifier: str
    scope_type: AuthorizationScopeType
    owner: str
    proof: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CyberAuthorization:
    owner: str
    scope_type: AuthorizationScopeType
    targets: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    forbidden_actions: tuple[str, ...] = tuple(sorted(FORBIDDEN_ACTIONS))
    approved_by: str = "local-owner"
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=30))
    id: str = field(default_factory=lambda: str(uuid4()))

    def is_active(self, now: datetime | None = None) -> bool:
        return (now or datetime.now(timezone.utc)) <= self.expires_at

    def to_policy_payload(self) -> dict[str, Any]:
        return {
            "owner": self.owner,
            "scope_type": self.scope_type.value,
            "targets": list(self.targets),
            "allowed_actions": list(self.allowed_actions),
            "forbidden_actions": list(self.forbidden_actions),
            "approved_by": self.approved_by,
            "expires_at": self.expires_at.isoformat(),
            "id": self.id,
        }


@dataclass(frozen=True)
class CyberLabActionRequest:
    action: str
    target: str
    authorization: CyberAuthorization | None = None
    dry_run: bool = True
    approved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class CyberLabDecision:
    decision: CyberLabDecisionType
    reason: str
    request_id: str
    audit_id: str
    dry_run: bool
    target: str | None = None

    @property
    def allowed(self) -> bool:
        return self.decision in {CyberLabDecisionType.ALLOWED, CyberLabDecisionType.DRY_RUN_ONLY}

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "request_id": self.request_id,
            "audit_id": self.audit_id,
            "dry_run": self.dry_run,
            "target": self.target,
        }


@dataclass(frozen=True)
class CyberLabAuditRecord:
    action: str
    target: str | None
    decision: CyberLabDecisionType
    reason: str
    dry_run: bool
    authorization_id: str | None = None
    request_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "action": self.action,
            "target": self.target,
            "decision": self.decision.value,
            "reason": self.reason,
            "dry_run": self.dry_run,
            "authorization_id": self.authorization_id,
            "request_id": self.request_id,
        }
