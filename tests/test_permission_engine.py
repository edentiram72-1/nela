from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from agents.base import AgentCommand, AgentResult, BaseAgent
from core.events import EventBus, EventTypes
from permissions import (
    AgentManifest,
    AuthenticatedUser,
    Capability,
    CapabilityRegistry,
    PermissionDecision,
    PermissionEngine,
    PermissionRequest,
    PermissionTier,
    ScopeGrant,
)


class LabAgent(BaseAgent):
    name = "lab"
    permission_manifest = AgentManifest(
        agent="lab",
        capabilities=(
            Capability("read_status", PermissionTier.T0),
            Capability("local_change", PermissionTier.T1),
            Capability("dangerous_change", PermissionTier.T2, requires_confirmation=True),
            Capability("sandbox_scan", PermissionTier.T3, scopes=("lab.local",), requires_confirmation=True),
            Capability("forbidden", PermissionTier.T4),
        ),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "ok")


def make_engine() -> tuple[PermissionEngine, EventBus]:
    events = EventBus()
    registry = CapabilityRegistry()
    registry.register_agent(LabAgent())
    return PermissionEngine(events=events, capability_registry=registry), events


class PermissionEngineTests(unittest.TestCase):
    def test_t0_and_t1_capabilities_are_granted_for_authenticated_user(self) -> None:
        engine, events = make_engine()

        t0 = engine.authorize(PermissionRequest(agent="lab", action="read_status"))
        t1 = engine.authorize(PermissionRequest(agent="lab", action="local_change"))

        self.assertTrue(t0.granted)
        self.assertEqual(t0.tier, PermissionTier.T0)
        self.assertTrue(t1.granted)
        self.assertEqual(t1.tier, PermissionTier.T1)
        self.assertEqual(len(engine.audit_log.records()), 2)
        self.assertIn(EventTypes.PERMISSION_GRANTED, [event.type for event in events.history()])

    def test_unknown_action_is_t4_denied_by_default(self) -> None:
        engine, events = make_engine()

        result = engine.authorize(PermissionRequest(agent="lab", action="not_declared"))

        self.assertFalse(result.granted)
        self.assertEqual(result.tier, PermissionTier.T4)
        self.assertEqual(result.decision, PermissionDecision.DENIED)
        self.assertIn(EventTypes.PERMISSION_DENIED, [event.type for event in events.history()])

    def test_t2_requires_confirmation_then_grants(self) -> None:
        engine, events = make_engine()

        blocked = engine.authorize(PermissionRequest(agent="lab", action="dangerous_change"))
        allowed = engine.authorize(PermissionRequest(agent="lab", action="dangerous_change", confirmed=True))

        self.assertFalse(blocked.granted)
        self.assertEqual(blocked.decision, PermissionDecision.CONFIRMATION_REQUIRED)
        self.assertTrue(allowed.granted)
        self.assertIn(EventTypes.PERMISSION_REQUESTED, [event.type for event in events.history()])

    def test_t3_requires_active_scoped_session_and_confirmation(self) -> None:
        engine, _events = make_engine()
        session = engine.create_scoped_session(
            allowed_agents=("lab",),
            allowed_tiers=(PermissionTier.T3,),
            scope_grants=(ScopeGrant("lab.local"),),
            reason="unit test lab session",
        )

        missing_scope = engine.authorize(
            PermissionRequest(agent="lab", action="sandbox_scan", confirmed=True)
        )
        unconfirmed = engine.authorize(
            PermissionRequest(agent="lab", action="sandbox_scan", scoped_session_id=session.id)
        )
        allowed = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="sandbox_scan",
                confirmed=True,
                scoped_session_id=session.id,
            )
        )

        self.assertFalse(missing_scope.granted)
        self.assertEqual(missing_scope.decision, PermissionDecision.SCOPE_VIOLATION)
        self.assertFalse(unconfirmed.granted)
        self.assertEqual(unconfirmed.decision, PermissionDecision.CONFIRMATION_REQUIRED)
        self.assertTrue(allowed.granted)
        self.assertEqual(allowed.scope_session_id, session.id)

    def test_expired_scoped_session_is_denied(self) -> None:
        engine, _events = make_engine()
        expired = datetime.now(timezone.utc) - timedelta(seconds=1)
        session = engine.create_scoped_session(
            allowed_agents=("lab",),
            allowed_tiers=(PermissionTier.T3,),
            scope_grants=(ScopeGrant("lab.local"),),
            expires_at=expired,
        )

        result = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="sandbox_scan",
                confirmed=True,
                scoped_session_id=session.id,
            )
        )

        self.assertFalse(result.granted)
        self.assertEqual(result.decision, PermissionDecision.SCOPE_VIOLATION)

    def test_kill_switch_and_lock_mode_allow_only_t0(self) -> None:
        engine, events = make_engine()

        engine.activate_kill_switch("test")
        self.assertTrue(engine.authorize(PermissionRequest(agent="lab", action="read_status")).granted)
        self.assertFalse(engine.authorize(PermissionRequest(agent="lab", action="local_change")).granted)

        engine.deactivate_kill_switch("test")
        engine.set_lock_mode(True, "test")
        self.assertTrue(engine.authorize(PermissionRequest(agent="lab", action="read_status")).granted)
        self.assertFalse(engine.authorize(PermissionRequest(agent="lab", action="local_change")).granted)

        event_types = [event.type for event in events.history()]
        self.assertIn(EventTypes.KILL_SWITCH_ACTIVATED, event_types)
        self.assertIn(EventTypes.LOCK_MODE_CHANGED, event_types)

    def test_unauthenticated_user_is_denied(self) -> None:
        engine, _events = make_engine()
        user = AuthenticatedUser(user_id="guest", authenticated=False, roles=())

        result = engine.authorize(PermissionRequest(agent="lab", action="read_status", user=user))

        self.assertFalse(result.granted)
        self.assertEqual(result.decision, PermissionDecision.AUTHENTICATION_REQUIRED)

    def test_records_action_result_to_audit_log_and_event_bus(self) -> None:
        engine, events = make_engine()
        request = PermissionRequest(agent="lab", action="local_change", task_id="task-1", plan_id="plan-1")
        permission = engine.authorize(request)

        engine.record_action_result(request, AgentResult(True, "done"), permission)

        self.assertTrue(permission.granted)
        self.assertEqual(engine.audit_log.records()[-1].result_message, "done")
        self.assertIn(EventTypes.ACTION_EXECUTED, [event.type for event in events.history()])


if __name__ == "__main__":
    unittest.main()
