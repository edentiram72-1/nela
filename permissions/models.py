"""Data models for NELA's Permission Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class PermissionTier(str, Enum):
    """Capability tiers used by every Agent action."""

    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"


class PermissionDecision(str, Enum):
    """Authorization outcome."""

    GRANTED = "granted"
    DENIED = "denied"
    CONFIRMATION_REQUIRED = "confirmation_required"
    AUTHENTICATION_REQUIRED = "authentication_required"
    LOCKED = "locked"
    KILL_SWITCH_ACTIVE = "kill_switch_active"
    SCOPE_VIOLATION = "scope_violation"


@dataclass(frozen=True)
class Capability:
    """One action an Agent may expose."""

    action: str
    tier: PermissionTier
    description: str = ""
    scopes: tuple[str, ...] = ()
    requires_confirmation: bool = False

    @property
    def needs_confirmation(self) -> bool:
        return self.requires_confirmation or self.tier in {PermissionTier.T2, PermissionTier.T3}


@dataclass(frozen=True)
class AgentManifest:
    """Declared capabilities for one Agent."""

    agent: str
    version: str = "1.0"
    capabilities: tuple[Capability, ...] = ()
    owner: str = "nela"

    def capability_for(self, action: str) -> Capability | None:
        for capability in self.capabilities:
            if capability.action == action:
                return capability
        return None


@dataclass(frozen=True)
class AuthenticatedUser:
    """Authenticated local user context."""

    user_id: str
    display_name: str = "Local user"
    authenticated: bool = True
    roles: tuple[str, ...] = ("owner",)


@dataclass(frozen=True)
class ScopeGrant:
    """One scoped permission inside a temporary session."""

    name: str
    values: tuple[str, ...] = ()

    def allows(self, value: str | None = None) -> bool:
        if not self.values:
            return True
        if value is None:
            return False
        return value in self.values


@dataclass(frozen=True)
class ScopedSession:
    """Time-limited permission session for higher-risk capabilities."""

    user_id: str
    allowed_agents: tuple[str, ...]
    allowed_tiers: tuple[PermissionTier, ...]
    scope_grants: tuple[ScopeGrant, ...] = ()
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=15))
    reason: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    active: bool = True

    def is_active(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return self.active and current <= self.expires_at

    def allows_agent(self, agent: str) -> bool:
        return "*" in self.allowed_agents or agent in self.allowed_agents

    def allows_tier(self, tier: PermissionTier) -> bool:
        return tier in self.allowed_tiers

    def has_scope(self, scope: str) -> bool:
        return any(grant.name == scope for grant in self.scope_grants)


@dataclass(frozen=True)
class PermissionRequest:
    """Runtime authorization request before one Agent command."""

    agent: str
    action: str
    payload: dict[str, Any] = field(default_factory=dict)
    task_id: str | None = None
    plan_id: str | None = None
    command_id: str = field(default_factory=lambda: str(uuid4()))
    user: AuthenticatedUser | None = None
    confirmed: bool = False
    scoped_session_id: str | None = None

    @property
    def target(self) -> str | None:
        value = (
            self.payload.get("target")
            or self.payload.get("application")
            or self.payload.get("resource")
            or self.payload.get("path")
        )
        return str(value) if value is not None else None


@dataclass(frozen=True)
class PermissionResult:
    """Authorization result consumed by the Dispatcher."""

    granted: bool
    decision: PermissionDecision
    tier: PermissionTier
    reason: str
    capability: Capability | None = None
    audit_id: str | None = None
    scope_session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "granted": self.granted,
            "decision": self.decision.value,
            "tier": self.tier.value,
            "reason": self.reason,
            "audit_id": self.audit_id,
            "scope_session_id": self.scope_session_id,
            "capability": self.capability.action if self.capability else None,
        }
