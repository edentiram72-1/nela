"""Permission Engine gateway for all Agent execution."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging

from agents.base import AgentResult, BaseAgent
from agents.process_isolation import IsolatedAgentProcessRunner, IsolatedProcessSupervisor
from core.events import Event, EventBus, EventTypes
from permissions.audit import AuditLog, AuditRecord, AuditWriteError
from permissions.confirmation import action_tuple_hash
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
from permissions.scope import validate_scopes


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
        self._isolated_processes = IsolatedProcessSupervisor()
        self._logger = logging.getLogger("nela.permissions")

    def register_agent(self, agent: BaseAgent) -> None:
        self.capabilities.register_agent(agent)

    def unregister_agent(self, agent_name: str) -> None:
        self.capabilities.unregister_agent(agent_name)

    def authorize(self, request: PermissionRequest) -> PermissionResult:
        user = request.user or self.default_user
        capability = self.capabilities.capability_for(request.agent, request.capability_id)
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
                reason=f"No capability manifest allows {request.agent}.{request.capability_id}.",
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

        if not capability.enabled:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.DENIED,
                reason=f"{request.agent}.{request.capability_id} is declared but disabled.",
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

        scope_result = validate_scopes(capability.scopes, request, scoped_session)
        if not scope_result.allowed:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.SCOPE_VIOLATION,
                reason=scope_result.reason,
                capability=capability,
            )

        if capability.needs_confirmation:
            confirmation_error = self._confirmation_error(request, capability.action)
            if confirmation_error is not None:
                decision = (
                    PermissionDecision.CONFIRMATION_REQUIRED
                    if not request.confirmed
                    else PermissionDecision.CONFIRMATION_MISMATCH
                )
                result = self._record(
                    request=request,
                    user=user,
                    tier=tier,
                    decision=decision,
                    reason=confirmation_error,
                    granted=False,
                    capability=capability,
                    scope_session_id=scoped_session.id if scoped_session else None,
                )
                event_type = EventTypes.PERMISSION_REQUESTED if result.decision == PermissionDecision.CONFIRMATION_REQUIRED else EventTypes.PERMISSION_DENIED
                self._publish(event_type, request, result)
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
        self._publish(EventTypes.PERMISSION_GRANTED if result.granted else EventTypes.PERMISSION_DENIED, request, result)
        return result

    def record_action_result(self, request: PermissionRequest, result: AgentResult, permission: PermissionResult) -> None:
        record = AuditRecord(
            agent=request.agent,
            action=request.action,
            capability=permission.capability.action if permission.capability else request.action,
            tier=permission.tier,
            decision=PermissionDecision.GRANTED if result.success else PermissionDecision.DENIED,
            reason="Agent execution completed." if result.success else "Agent execution failed.",
            granted=permission.granted,
            user_id=(request.user or self.default_user).user_id,
            target=request.target,
            session_id=permission.scope_session_id,
            task_id=request.task_id,
            plan_id=request.plan_id,
            command_id=request.command_id,
            scope_session_id=permission.scope_session_id,
            result_success=result.success,
            result_message=result.message,
        )
        try:
            self.audit_log.append(record)
        except AuditWriteError:
            if permission.tier in {PermissionTier.T2, PermissionTier.T3}:
                raise
            self._logger.exception("audit_result_write_failed agent=%s action=%s", request.agent, request.action)
            return
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
        revoked_sessions = self.revoke_all_scoped_sessions()
        terminated_processes = self._isolated_processes.terminate_all()
        self._logger.warning(
            "permission_kill_switch_active reason=%s revoked_sessions=%s terminated_processes=%s",
            reason,
            revoked_sessions,
            terminated_processes,
        )
        self.events.publish(
            Event(
                type=EventTypes.KILL_SWITCH_ACTIVATED,
                source="permissions.engine",
                payload={
                    "active": True,
                    "reason": reason,
                    "revoked_sessions": revoked_sessions,
                    "terminated_processes": terminated_processes,
                },
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

    def revoke_all_scoped_sessions(self) -> int:
        count = len(self._scoped_sessions)
        self._scoped_sessions.clear()
        return count

    def register_isolated_runner(self, runner: IsolatedAgentProcessRunner) -> str:
        return self._isolated_processes.register(runner)

    def unregister_isolated_runner(self, token: str) -> None:
        self._isolated_processes.unregister(token)

    def active_isolated_runner_count(self) -> int:
        return self._isolated_processes.active_count()

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
        record = AuditRecord(
            agent=request.agent,
            action=request.action,
            capability=capability.action if capability else request.capability_id,
            tier=tier,
            decision=decision,
            reason=reason,
            granted=granted,
            user_id=user.user_id,
            target=request.target,
            session_id=scope_session_id,
            task_id=request.task_id,
            plan_id=request.plan_id,
            command_id=request.command_id,
            scope_session_id=scope_session_id,
        )
        try:
            record = self.audit_log.append(record)
        except AuditWriteError:
            if tier in {PermissionTier.T2, PermissionTier.T3}:
                return PermissionResult(
                    granted=False,
                    decision=PermissionDecision.DENIED,
                    tier=tier,
                    reason="Audit write failed; action denied fail-closed.",
                    capability=capability,
                )
            self._logger.exception("audit_decision_write_failed agent=%s action=%s", request.agent, request.action)
            return PermissionResult(
                granted=granted,
                decision=decision,
                tier=tier,
                reason=f"{reason} Audit write failed; continuing under T0/T1 diagnostic policy.",
                capability=capability,
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

    def _confirmation_error(self, request: PermissionRequest, capability_id: str) -> str | None:
        if not request.confirmed:
            return f"{request.agent}.{request.action} requires user confirmation."
        expires_at = _parse_datetime(request.confirmation_expires_at)
        if expires_at is None:
            return "Confirmation is missing a bound expiration."
        if datetime.now(timezone.utc) > expires_at:
            return "Confirmation expired before execution."
        expected = action_tuple_hash(
            agent=request.agent,
            capability=capability_id,
            action=request.action,
            target=request.target,
            parameters=request.payload,
            session=request.scoped_session_id,
            expires_at=expires_at,
        )
        if request.confirmation_action_hash != expected:
            return "Confirmation does not match the exact action tuple."
        return None

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


def _parse_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            return None
    return None
