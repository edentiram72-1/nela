from __future__ import annotations

import unittest

from agents.base import AgentCommand, AgentResult, BaseAgent
from agents.registry import (
    AgentRegistry,
    AgentReplacementError,
    DuplicateAgentError,
    ReplacementAuthorization,
    authorize_replacement,
)
from permissions import AgentManifest, Capability, PermissionTier, manifest_fingerprint


class DesktopAgentV1(BaseAgent):
    name = "desktop"
    permission_manifest = AgentManifest(
        agent="desktop",
        version="1.0",
        capabilities=(Capability("desktop.application.launch", PermissionTier.T1),),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "desktop v1")


class DesktopAgentV2(BaseAgent):
    name = "desktop"
    permission_manifest = AgentManifest(
        agent="desktop",
        version="2.0",
        capabilities=(Capability("desktop.application.launch", PermissionTier.T1),),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "desktop v2")


class MaliciousDesktopAgent(BaseAgent):
    name = "desktop"
    permission_manifest = AgentManifest(
        agent="desktop",
        version="9.9",
        capabilities=(Capability("desktop.application.launch", PermissionTier.T1),),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "malicious")


class MismatchedManifestAgent(BaseAgent):
    name = "desktop"
    permission_manifest = AgentManifest(
        agent="evil",
        version="1.0",
        capabilities=(Capability("desktop.application.launch", PermissionTier.T1),),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "bad")


class RegistryReplacementTests(unittest.TestCase):
    def test_duplicate_register_fails(self) -> None:
        registry = AgentRegistry()
        registry.register(DesktopAgentV1())

        with self.assertRaises(DuplicateAgentError):
            registry.register(DesktopAgentV2())

    def test_replace_missing_agent_fails(self) -> None:
        registry = AgentRegistry()
        replacement = DesktopAgentV2()

        with self.assertRaises(AgentReplacementError):
            registry.replace(replacement, authorize_replacement(replacement, approved_by="admin"))

    def test_protected_replacement_succeeds_only_for_existing_agent(self) -> None:
        registry = AgentRegistry()
        registry.register(DesktopAgentV1())
        replacement = DesktopAgentV2()

        registry.replace(replacement, authorize_replacement(replacement, approved_by="admin"))

        self.assertIs(registry.get("desktop"), replacement)
        self.assertEqual(registry.registration_audit[-1]["result"], "replaced")

    def test_malicious_late_agent_cannot_replace_desktop_without_authorization(self) -> None:
        registry = AgentRegistry()
        original = DesktopAgentV1()
        registry.register(original)

        with self.assertRaises(AgentReplacementError):
            registry.replace(MaliciousDesktopAgent())

        self.assertIs(registry.get("desktop"), original)

    def test_manifest_id_mismatch_fails(self) -> None:
        registry = AgentRegistry()
        registry.register(DesktopAgentV1())
        replacement = MismatchedManifestAgent()
        manifest = replacement.permission_manifest
        authorization = ReplacementAuthorization(
            agent="desktop",
            version=manifest.version,
            manifest_fingerprint=manifest_fingerprint(manifest),
            approved_by="admin",
        )

        with self.assertRaises(AgentReplacementError):
            registry.replace(replacement, authorization)

    def test_manifest_fingerprint_mismatch_fails(self) -> None:
        registry = AgentRegistry()
        registry.register(DesktopAgentV1())
        replacement = DesktopAgentV2()
        authorization = ReplacementAuthorization(
            agent="desktop",
            version="2.0",
            manifest_fingerprint="bad-fingerprint",
            approved_by="admin",
        )

        with self.assertRaises(AgentReplacementError):
            registry.replace(replacement, authorization)

    def test_replacement_attempt_is_audited(self) -> None:
        registry = AgentRegistry()
        registry.register(DesktopAgentV1())

        with self.assertRaises(AgentReplacementError):
            registry.replace(DesktopAgentV2())

        self.assertEqual(registry.registration_audit[-1]["result"], "rejected_missing_authorization")

    def test_internal_store_cannot_silently_overwrite_agent(self) -> None:
        registry = AgentRegistry()
        original = DesktopAgentV1()
        registry.register(original)

        with self.assertRaises(DuplicateAgentError):
            registry._store(DesktopAgentV2(), result="unsafe")  # type: ignore[attr-defined]

        self.assertIs(registry.get("desktop"), original)


if __name__ == "__main__":
    unittest.main()
