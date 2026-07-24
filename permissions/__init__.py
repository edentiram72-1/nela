"""Permission Engine public API."""

from permissions.audit import AuditLog, AuditRecord
from permissions.engine import PermissionEngine
from permissions.registry import CapabilityRegistry, default_capability_registry
from permissions.confirmation import action_tuple_hash
from permissions.models import (
    AuthenticatedUser,
    Capability,
    AgentManifest,
    PermissionDecision,
    PermissionRequest,
    PermissionResult,
    PermissionTier,
    ScopeGrant,
    ScopedSession,
)

__all__ = [
    "AgentManifest",
    "AuthenticatedUser",
    "AuditLog",
    "AuditRecord",
    "Capability",
    "CapabilityRegistry",
    "PermissionDecision",
    "PermissionEngine",
    "PermissionRequest",
    "PermissionResult",
    "PermissionTier",
    "ScopeGrant",
    "ScopedSession",
    "default_capability_registry",
    "action_tuple_hash",
]
