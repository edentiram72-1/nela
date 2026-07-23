"""Permission Engine gateway for all Agent execution."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging

from agents.base import AgentResult, BaseAgent
from core.events import Event, EventBus, EventTypes
from permissions.audit import AuditLog, AuditRecord
from permissions.models import (
    AuthenticatedUser,
    PermissionDecision,
    PermissionRequest,
    PermissionResult,
    PermissionTier,
    ScopeGrant,
    ScopedSession,
)
from permissions.registry import CapabilityRegistry, default_capability_registry


class PermissionEngine:
    """Single authorization gateway before Agent commands execute."""

    def __init__(
        self,
        events: EventBus | None = None,
        capability_registry: CapabilityRegistry | None = None,
        audit_log: AuditLog | None = None,
        default_user: AuthenticatedUser | None = None,
    ) -> None:
        self.events = events or EventBus()
        self.capabilities = capability_registry or default_capability_registry()
        self.audit_log = audit_log or AuditLog()
        self.default_user = default_user or AuthenticatedUser(user_id="local-owner", display_name="Local owner")
        self.kill_switch_active = False
        self.lock_mode_active = False
        self._scoped_sessions: dict[str, ScopedSession] = {}
        self._logger = logging.getLogger("nela.permissions")

    def register_agent(self, agent: BaseAgent) -> None:
        self.capabilities.register_agent(agent)

    def unregister_agent(self, agent_name: str) -> None:
        self.capabilities.unregister_agent(agent_name)

    def authorize(self, request: PermissionRequest) -> PermissionResult:
        user = request.user or self.default_user
        capability = self.capabilities.capability_for(request.agent, request.action)
        tier = capability.tier if capability else PermissionTier.T4

        if not user.authenticated:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.AUTHENTICATION_REQUIRED,
                reason="Authenticated user is required.",
            )

        if capability is None:
            return self._deny(
                request=request,
                user=user,
                tier=PermissionTier.T4,
                decision=PermissionDecision.DENIED,
                reason=f"No capability manifest allows {request.agent}.{request.action}.",
            )

        if tier == PermissionTier.T4:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.DENIED,
                reason=f"{request.agent}.{request.action} is forbidden.",
                capability=capability,
            )

        if self.kill_switch_active and tier != PermissionTier.T0:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.KILL_SWITCH_ACTIVE,
                reason="Kill switch is active; only T0 reads are allowed.",
                capability=capability,
            )

        if self.lock_mode_active and tier != PermissionTier.T0:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.LOCKED,
                reason="Lock mode is active; only T0 reads are allowed.",
                capability=capability,
            )

        scoped_session = self._resolve_scoped_session(request)
        if tier == PermissionTier.T3:
            scope_result = self._validate_t3_scope(request, user, scoped_session)
            if scope_result is not None:
                return self._deny(
                    request=request,
                    user=user,
                    tier=tier,
                    decision=PermissionDecision.SCOPE_VIOLATION,
                    reason=scope_result,
                    capability=capability,
                )

        for scope in capability.scopes:
            if scoped_session is None or not scoped_session.has_scope(scope):
                return self._deny(
                    request=request,
                    user=user,
                    tier=tier,
                    decision=PermissionDecision.SCOPE_VIOLATION,
                    reason=f"Missing scoped session grant for scope '{scope}'.",
                    capability=capability,
                )

        if capability.needs_confirmation and not request.confirmed:
            result = self._record(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.CONFIRMATION_REQUIRED,
                reason=f"{request.agent}.{request.action} requires user confirmation.",
                granted=False,
                capability=capability,
                scope_session_id=scoped_session.id if scoped_session else None,
            )
            self._publish(EventTypes.PERMISSION_REQUESTED, request, result)
            return result

        result = self._record(
            request=request,
            user=user,
            tier=tier,
            decision=PermissionDecision.GRANTED,
            reason=f"{request.agent}.{request.action} authorized.",
            granted=True,
            capability=capability,
            scope_session_id=scoped_session.id if scoped_session else None,
        )
        self._publish(EventTypes.PERMISSION_GRANTED, request, result)
        return result

    def record_action_result(self, request: PermissionRequest, result: AgentResult, permission: PermissionResult) -> None:
        record = AuditRecord(
            agent=request.agent,
            action=request.action,
            tier=permission.tier,
            decision=PermissionDecision.GRANTED if result.success else PermissionDecision.DENIED,
            reason="Agent execution completed." if result.success else "Agent execution failed.",
            granted=permission.granted,
            user_id=(request.user or self.default_user).user_id,
            target=request.target,
            task_id=request.task_id,
            plan_id=request.plan_id,
            command_id=request.command_id,
            scope_session_id=permission.scope_session_id,
            result_success=result.success,
            result_message=result.message,
        )
        self.audit_log.append(record)
        self.events.publish(
            Event(
                type=EventTypes.ACTION_EXECUTED,
                source="permissions.engine",
                payload={
                    "audit_id": record.id,
                    "agent": request.agent,
                    "action": request.action,
                    "tier": permission.tier.value,
                    "success": result.success,
                    "task_id": request.task_id,
                    "plan_id": request.plan_id,
                },
            )
        )

    def create_scoped_session(
        self,
        user: AuthenticatedUser | None = None,
        allowed_agents: tuple[str, ...] = (),
        allowed_tiers: tuple[PermissionTier, ...] = (),
        scope_grants: tuple[ScopeGrant, ...] = (),
        expires_at: datetime | None = None,
        reason: str = "",
    ) -> ScopedSession:
        authenticated_user = user or self.default_user
        session = ScopedSession(
            user_id=authenticated_user.user_id,
            allowed_agents=allowed_agents or ("*",),
            allowed_tiers=allowed_tiers or (PermissionTier.T0, PermissionTier.T1),
            scope_grants=scope_grants,
            expires_at=expires_at or datetime.now(timezone.utc) + timedelta(minutes=15),
            reason=reason,
        )
        self._scoped_sessions[session.id] = session
        return session

    def revoke_scoped_session(self, session_id: str) -> bool:
        return self._scoped_sessions.pop(session_id, None) is not None

    def scoped_sessions(self) -> tuple[ScopedSession, ...]:
        return tuple(self._scoped_sessions.values())

    def activate_kill_switch(self, reason: str = "") -> None:
        self.kill_switch_active = True
        self._logger.warning("permission_kill_switch_active reason=%s", reason)
        self.events.publish(
            Event(
                type=EventTypes.KILL_SWITCH_ACTIVATED,
                source="permissions.engine",
                payload={"active": True, "reason": reason},
            )
        )

    def deactivate_kill_switch(self, reason: str = "") -> None:
        self.kill_switch_active = False
        self.events.publish(
            Event(
                type=EventTypes.KILL_SWITCH_DEACTIVATED,
                source="permissions.engine",
                payload={"active": False, "reason": reason},
            )
        )

    def set_lock_mode(self, active: bool, reason: str = "") -> None:
        self.lock_mode_active = active
        self.events.publish(
            Event(
                type=EventTypes.LOCK_MODE_CHANGED,
                source="permissions.engine",
                payload={"active": active, "reason": reason},
            )
        )

    def _validate_t3_scope(
        self,
        request: PermissionRequest,
        user: AuthenticatedUser,
        session: ScopedSession | None,
    ) -> str | None:
        if session is None:
            return "T3 actions require an active scoped session."
        if session.user_id != user.user_id:
            return "Scoped session belongs to a different user."
        if not session.allows_agent(request.agent):
            return f"Scoped session does not allow Agent '{request.agent}'."
        if not session.allows_tier(PermissionTier.T3):
            return "Scoped session does not allow T3 actions."
        return None

    def _resolve_scoped_session(self, request: PermissionRequest) -> ScopedSession | None:
        if not request.scoped_session_id:
            return None
        session = self._scoped_sessions.get(request.scoped_session_id)
        if session is None or not session.is_active():
            return None
        return session

    def _deny(
        self,
        request: PermissionRequest,
        user: AuthenticatedUser,
        tier: PermissionTier,
        decision: PermissionDecision,
        reason: str,
        capability=None,
    ) -> PermissionResult:
        result = self._record(
            request=request,
            user=user,
            tier=tier,
            decision=decision,
            reason=reason,
            granted=False,
            capability=capability,
        )
        event_type = EventTypes.SCOPE_VIOLATION if decision == PermissionDecision.SCOPE_VIOLATION else EventTypes.PERMISSION_DENIED
        self._publish(event_type, request, result)
        return result

    def _record(
        self,
        request: PermissionRequest,
        user: AuthenticatedUser,
        tier: PermissionTier,
        decision: PermissionDecision,
        reason: str,
        granted: bool,
        capability=None,
        scope_session_id: str | None = None,
    ) -> PermissionResult:
        record = self.audit_log.append(
            AuditRecord(
                agent=request.agent,
                action=request.action,
                tier=tier,
                decision=decision,
                reason=reason,
                granted=granted,
                user_id=user.user_id,
                target=request.target,
                task_id=request.task_id,
                plan_id=request.plan_id,
                command_id=request.command_id,
                scope_session_id=scope_session_id,
            )
        )
        return PermissionResult(
            granted=granted,
            decision=decision,
            tier=tier,
            reason=reason,
            capability=capability,
            audit_id=record.id,
            scope_session_id=scope_session_id,
        )

    def _publish(self, event_type: str, request: PermissionRequest, result: PermissionResult) -> None:
        self.events.publish(
            Event(
                type=event_type,
                source="permissions.engine",
                payload={
                    "agent": request.agent,
                    "action": request.action,
                    "task_id": request.task_id,
                    "plan_id": request.plan_id,
                    **result.to_dict(),
                },
            )
        )
