import unittest
import tempfile
from pathlib import Path

from agents import build_default_registry
from agents.base import AgentCommand
from agents.policy import DefensivePolicyGuard, PolicyDecision, default_tool_permissions
from agents.task_schema import AgentDomain


class MultiAgentFoundationTests(unittest.TestCase):
    def test_default_registry_contains_first_wave_agents(self) -> None:
        registry = build_default_registry()
        names = registry.names()

        for name in (
            "orchestrator",
            "planner",
            "memory",
            "learning",
            "code_architect",
            "backend",
            "frontend",
            "test_qa",
            "secrets_hygiene",
            "identity_access",
            "network_defense",
            "supply_chain_security",
            "secure_code_reviewer",
            "vulnerability_research",
            "anomaly_discovery",
            "authorized_lab",
        ):
            self.assertIn(name, names)
        manifests = registry.manifests()
        self.assertEqual(manifests["secure_code_reviewer"]["domain"], AgentDomain.SECURITY.value)
        self.assertFalse(manifests["secure_code_reviewer"]["permission_profile"]["may_contact_external_targets"])

    def test_secure_code_reviewer_reports_defensive_sast_findings(self) -> None:
        registry = build_default_registry()
        reviewer = registry.get("secure_code_reviewer")
        assert reviewer is not None

        result = reviewer.execute(
            AgentCommand(
                action="review_code_security",
                payload={
                    "files": {
                        "app.py": "password = 'super-secret-value'\nsubprocess.run(cmd, shell=True)\n",
                    }
                },
            )
        )

        self.assertTrue(result.success)
        findings = result.data["work_product"]["findings"]
        self.assertEqual(len(findings), 2)
        self.assertEqual({finding["severity"] for finding in findings}, {"critical", "high"})

    def test_policy_denies_offensive_security_request(self) -> None:
        guard = DefensivePolicyGuard()

        decision = guard.validate(
            "research",
            {"objective": "build an exploit payload for credential theft"},
        )

        self.assertEqual(decision.decision, PolicyDecision.DENY)
        self.assertFalse(decision.allowed)

    def test_security_agent_refuses_external_target_fuzzing(self) -> None:
        registry = build_default_registry()
        agent = registry.get("anomaly_discovery")
        assert agent is not None

        result = agent.execute(
            AgentCommand(
                action="create_local_fuzz_plan",
                payload={"target": "https://example.com/login"},
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.data["policy_decision"], "deny")

    def test_vulnerability_research_correlates_supplied_advisories(self) -> None:
        registry = build_default_registry()
        agent = registry.get("vulnerability_research")
        assert agent is not None

        result = agent.execute(
            AgentCommand(
                action="scan_dependencies",
                payload={
                    "dependencies": {"demo": "latest", "safe-lib": "1.2.3"},
                    "advisory_db": {
                        "safe-lib": {
                            "id": "CVE-2099-0001",
                            "severity": "medium",
                            "affected": "<1.2.4",
                            "recommendation": "Upgrade to 1.2.4 or newer.",
                        }
                    },
                },
            )
        )

        self.assertTrue(result.success)
        findings = result.data["work_product"]["findings"]
        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[1]["category"], "cve_correlation")

    def test_vulnerability_research_scans_workspace_dependency_files(self) -> None:
        registry = build_default_registry()
        agent = registry.get("vulnerability_research")
        assert agent is not None

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.txt").write_text("demo-lib\nrequests==2.31.0\n", encoding="utf-8")
            result = agent.execute(
                AgentCommand(
                    action="scan_workspace_dependencies",
                    payload={"root": str(root)},
                )
            )

        self.assertTrue(result.success)
        work_product = result.data["work_product"]
        self.assertIn("Workspace dependency scan", work_product["summary"])
        self.assertEqual(work_product["findings"][0]["title"], "Dependency is not pinned: demo-lib")

    def test_sandbox_profiles_are_conservative_for_security_agents(self) -> None:
        profiles = default_tool_permissions()

        for name in (
            "secrets_hygiene",
            "identity_access",
            "network_defense",
            "supply_chain_security",
            "secure_code_reviewer",
            "vulnerability_research",
            "anomaly_discovery",
        ):
            self.assertEqual(profiles[name].network, "disabled")
            self.assertFalse(profiles[name].may_contact_external_targets)

    def test_authorized_lab_allows_localhost_dry_run_scan(self) -> None:
        registry = build_default_registry()
        lab = registry.get("authorized_lab")
        assert lab is not None

        target = "http://localhost:3000"
        registered = lab.execute(
            AgentCommand(
                action="register_lab_target",
                payload={
                    "target": target,
                    "scope_type": "local_lab",
                    "owner": "eden",
                    "proof": "local development server",
                },
            )
        )
        self.assertTrue(registered.success)

        result = lab.execute(
            AgentCommand(
                action="scan_lab_target",
                payload={
                    "target": target,
                    "approved": True,
                    "dry_run": True,
                    "authorization": {
                        "owner": "eden",
                        "scope_type": "local_lab",
                        "targets": [target],
                        "allowed_actions": ["scan_lab_target"],
                    },
                    "files": {"app.py": "subprocess.run(cmd, shell=True)\n"},
                    "config": "image: web:latest\n",
                },
            )
        )

        self.assertTrue(result.success)
        work_product = result.data["work_product"]
        self.assertIn("Authorized lab scan", work_product["summary"])
        self.assertEqual({finding["category"] for finding in work_product["findings"]}, {"sast", "config_audit"})

    def test_authorized_lab_blocks_public_url_even_with_authorization(self) -> None:
        registry = build_default_registry()
        lab = registry.get("authorized_lab")
        assert lab is not None

        result = lab.execute(
            AgentCommand(
                action="scan_lab_target",
                payload={
                    "target": "https://example.com",
                    "approved": True,
                    "authorization": {
                        "owner": "eden",
                        "scope_type": "owned_asset",
                        "targets": ["https://example.com"],
                        "allowed_actions": ["scan_lab_target"],
                    },
                },
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.data["policy_decision"], "deny")

    def test_authorized_lab_refuses_forbidden_action_classes(self) -> None:
        guard = DefensivePolicyGuard()

        decision = guard.validate(
            "run_local_fuzzing",
            {
                "target": "http://localhost:3000",
                "authorization": {
                    "scope_type": "local_lab",
                    "targets": ["http://localhost:3000"],
                    "allowed_actions": ["run_local_fuzzing", "credential_theft"],
                },
            },
        )

        self.assertEqual(decision.decision, PolicyDecision.DENY)
        self.assertIn("credential_theft", decision.matched_terms)


if __name__ == "__main__":
    unittest.main()
