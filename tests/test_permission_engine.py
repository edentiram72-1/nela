from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
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
    action_tuple_hash,
    manifest_fingerprint,
)
from permissions.registry import ManifestRegistrationError


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


class FileAgent(BaseAgent):
    name = "file_agent"
    permission_manifest = AgentManifest(
        agent="file_agent",
        capabilities=(
            Capability("file.write", PermissionTier.T2, scopes=("filesystem.project",), requires_confirmation=True),
        ),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "ok")


def make_engine() -> tuple[PermissionEngine, EventBus]:
    events = EventBus()
    registry = CapabilityRegistry()
    registry.register_agent(LabAgent())
    registry.register_agent(FileAgent())
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
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        payload = {"confirmation_expires_at": expires_at}
        confirmation_hash = action_tuple_hash(
            agent="lab",
            capability="dangerous_change",
            action="dangerous_change",
            target=None,
            parameters=payload,
            expires_at=expires_at,
        )

        blocked = engine.authorize(PermissionRequest(agent="lab", action="dangerous_change"))
        allowed = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="dangerous_change",
                payload=payload,
                confirmed=True,
                confirmation_action_hash=confirmation_hash,
                confirmation_expires_at=expires_at,
            )
        )

        self.assertFalse(blocked.granted)
        self.assertEqual(blocked.decision, PermissionDecision.CONFIRMATION_REQUIRED)
        self.assertTrue(allowed.granted)
        self.assertIn(EventTypes.PERMISSION_REQUESTED, [event.type for event in events.history()])

    def test_t3_requires_active_scoped_session_and_confirmation(self) -> None:
        engine, _events = make_engine()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        payload = {"confirmation_expires_at": expires_at}
        session = engine.create_scoped_session(
            allowed_agents=("lab",),
            allowed_tiers=(PermissionTier.T3,),
            scope_grants=(ScopeGrant("lab.local"),),
            reason="unit test lab session",
        )
        confirmation_hash = action_tuple_hash(
            agent="lab",
            capability="sandbox_scan",
            action="sandbox_scan",
            target=None,
            parameters=payload,
            session=session.id,
            expires_at=expires_at,
        )

        missing_scope = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="sandbox_scan",
                payload=payload,
                confirmed=True,
                confirmation_action_hash=confirmation_hash,
                confirmation_expires_at=expires_at,
            )
        )
        unconfirmed = engine.authorize(
            PermissionRequest(agent="lab", action="sandbox_scan", scoped_session_id=session.id)
        )
        allowed = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="sandbox_scan",
                payload=payload,
                confirmed=True,
                confirmation_action_hash=confirmation_hash,
                confirmation_expires_at=expires_at,
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
        payload = {"confirmation_expires_at": datetime.now(timezone.utc) + timedelta(minutes=5)}

        result = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="sandbox_scan",
                payload=payload,
                confirmed=True,
                confirmation_action_hash="expired-session-hash",
                confirmation_expires_at=payload["confirmation_expires_at"],
                scoped_session_id=session.id,
            )
        )

        self.assertFalse(result.granted)
        self.assertEqual(result.decision, PermissionDecision.SCOPE_VIOLATION)

    def test_kill_switch_and_lock_mode_allow_only_t0(self) -> None:
        engine, events = make_engine()
        engine.create_scoped_session(allowed_agents=("lab",), allowed_tiers=(PermissionTier.T3,))

        engine.activate_kill_switch("test")
        self.assertEqual(engine.scoped_sessions(), ())
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

    def test_filesystem_scope_canonicalizes_and_blocks_symlink_escape(self) -> None:
        engine, _events = make_engine()
        with tempfile.TemporaryDirectory() as project, tempfile.TemporaryDirectory() as outside:
            project_path = Path(project)
            outside_path = Path(outside)
            symlink = project_path / "link-out"
            symlink.symlink_to(outside_path / "target.txt")
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            session = engine.create_scoped_session(
                allowed_agents=("file_agent",),
                allowed_tiers=(PermissionTier.T2,),
                scope_grants=(ScopeGrant("filesystem.project", (str(project_path),)),),
            )
            payload = {"path": str(symlink), "confirmation_expires_at": expires_at}
            confirmation_hash = action_tuple_hash(
                agent="file_agent",
                capability="file.write",
                action="file.write",
                target=str(symlink),
                parameters=payload,
                session=session.id,
                expires_at=expires_at,
            )

            result = engine.authorize(
                PermissionRequest(
                    agent="file_agent",
                    action="file.write",
                    payload=payload,
                    confirmed=True,
                    confirmation_action_hash=confirmation_hash,
                    confirmation_expires_at=expires_at,
                    scoped_session_id=session.id,
                )
            )

            self.assertFalse(result.granted)
            self.assertEqual(result.decision, PermissionDecision.SCOPE_VIOLATION)

    def test_capability_registry_rejects_duplicate_manifest_by_default(self) -> None:
        registry = CapabilityRegistry()
        manifest = AgentManifest(agent="duplicate", capabilities=(Capability("status", PermissionTier.T0),))
        registry.register_manifest(manifest)

        with self.assertRaises(ManifestRegistrationError):
            registry.register_manifest(manifest)

        self.assertEqual(registry.manifest_for("duplicate"), manifest)
        self.assertEqual(registry.registration_audit[-1]["result"], "rejected_duplicate")

    def test_capability_registry_rejects_implicit_baseline_replacement(self) -> None:
        registry = CapabilityRegistry(
            (
                AgentManifest(
                    agent="desktop",
                    capabilities=(Capability("desktop.application.launch", PermissionTier.T1),),
                ),
            )
        )

        with self.assertRaises(ManifestRegistrationError):
            registry.register_agent(
                type(
                    "ReplacementDesktop",
                    (BaseAgent,),
                    {
                        "name": "desktop",
                        "permission_manifest": AgentManifest(
                            agent="desktop",
                            version="2.0",
                            capabilities=(Capability("desktop.application.launch", PermissionTier.T1),),
                        ),
                        "execute": lambda self, command: AgentResult(True, "ok"),
                    },
                )()
            )

        self.assertEqual(registry.registration_audit[-1]["result"], "rejected_duplicate")

    def test_capability_registry_replacement_requires_manifest_fingerprint(self) -> None:
        registry = CapabilityRegistry()
        original = AgentManifest(agent="replaceable", capabilities=(Capability("status", PermissionTier.T0),))
        replacement = AgentManifest(
            agent="replaceable",
            version="2.0",
            capabilities=(Capability("status", PermissionTier.T0),),
        )
        registry.register_manifest(original)

        with self.assertRaises(ManifestRegistrationError):
            registry.replace_manifest(replacement, expected_fingerprint="bad")

        registry.replace_manifest(replacement, expected_fingerprint=manifest_fingerprint(replacement))

        self.assertEqual(registry.manifest_for("replaceable"), replacement)
        self.assertEqual(registry.registration_audit[-1]["result"], "replaced")

    def test_capability_registry_rejects_policy_tier_downgrade(self) -> None:
        registry = CapabilityRegistry()

        with self.assertRaises(ManifestRegistrationError):
            registry.register_manifest(
                AgentManifest(
                    agent="bad_terminal",
                    capabilities=(Capability("terminal.command.execute_allowlisted", PermissionTier.T0),),
                )
            )

    def test_disabled_foundation_capability_is_denied(self) -> None:
        engine = PermissionEngine(events=EventBus())

        result = engine.authorize(
            PermissionRequest(agent="terminal", action="execute_allowlisted", capability="terminal.command.execute_allowlisted")
        )

        self.assertFalse(result.granted)
        self.assertEqual(result.decision, PermissionDecision.DENIED)
        self.assertIn("disabled", result.reason)


if __name__ == "__main__":
    unittest.main()
