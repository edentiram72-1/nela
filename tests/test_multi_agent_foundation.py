import unittest

from agents import build_default_registry
from agents.base import AgentCommand
from agents.policy import DefensivePolicyGuard, PolicyDecision, default_tool_permissions
from agents.task_schema import AgentDomain


class MultiAgentFoundationTests(unittest.TestCase):
    def test_default_registry_contains_first_wave_agents(self) -> None:
        registry = build_default_registry()

        self.assertEqual(
            registry.names(),
            (
                "anomaly_discovery",
                "backend",
                "code_architect",
                "frontend",
                "learning",
                "memory",
                "orchestrator",
                "planner",
                "secure_code_reviewer",
                "test_qa",
                "vulnerability_research",
            ),
        )
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

    def test_sandbox_profiles_are_conservative_for_security_agents(self) -> None:
        profiles = default_tool_permissions()

        for name in ("secure_code_reviewer", "vulnerability_research", "anomaly_discovery"):
            self.assertEqual(profiles[name].network, "disabled")
            self.assertFalse(profiles[name].may_contact_external_targets)


if __name__ == "__main__":
    unittest.main()
