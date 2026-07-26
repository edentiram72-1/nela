from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from agents.base import AgentCommand
from agents.factory import build_default_agents, build_default_registry
from brain.dispatcher import AgentDispatcher
from brain.planner import Task
from core.events import EventBus
from permissions import PermissionTier, ScopeGrant, action_tuple_hash


EXPECTED_AGENT_NAMES = {
    "orchestrator",
    "planner",
    "memory",
    "learning",
    "quality_self_evaluation",
    "code_architect",
    "backend",
    "frontend",
    "mobile",
    "devops",
    "code_reviewer",
    "test_qa",
    "test_engineer",
    "documentation",
    "llm_engineer",
    "ml_engineer",
    "data_engineer",
    "research",
    "documentation_researcher",
    "trend_monitor",
    "security_researcher",
    "cyber_defense",
    "secrets_hygiene",
    "identity_access",
    "network_defense",
    "supply_chain_security",
    "secure_code_reviewer",
    "vulnerability_research",
    "infrastructure_security",
    "threat_intelligence",
    "sentinel",
    "incident_commander",
    "containment",
    "deception",
    "forensics",
    "threat_hunter",
    "red_team_simulator",
    "blue_team",
    "purple_team",
    "exploit_validation",
    "detection_engineering",
    "recovery",
    "anomaly_discovery",
    "browser",
    "terminal",
    "github",
    "files",
    "automation",
}


class MultiAgentExpansionTests(unittest.TestCase):
    def test_default_registry_contains_requested_agent_families(self) -> None:
        registry = build_default_registry()

        self.assertTrue(EXPECTED_AGENT_NAMES.issubset(set(registry.names())))
        self.assertEqual(len(registry.names()), len(set(registry.names())))

    def test_specialist_agents_expose_permission_manifests(self) -> None:
        specialist_agents = [agent for agent in build_default_agents() if hasattr(agent, "permission_manifest")]

        self.assertGreaterEqual(len(specialist_agents), 35)
        for agent in specialist_agents:
            manifest = agent.permission_manifest
            self.assertEqual(manifest.agent, agent.name)
            self.assertIsNotNone(manifest.capability_for("describe_capabilities"))

    def test_secure_code_reviewer_finds_local_sast_issue(self) -> None:
        registry = build_default_registry()
        reviewer = registry.get("secure_code_reviewer")
        self.assertIsNotNone(reviewer)

        result = reviewer.execute(
            AgentCommand(
                action="review_code_security",
                payload={"files": {"app.py": "import subprocess\nsubprocess.run(cmd, shell=True)\n"}},
            )
        )

        self.assertTrue(result.success)
        findings = result.data["work_product"]["findings"]
        self.assertEqual(findings[0]["title"], "Shell execution enabled")

    def test_new_defensive_security_specialists_return_findings(self) -> None:
        registry = build_default_registry()
        cases = (
            ("secrets_hygiene", "review_secrets_hygiene", "api_key = 'supersecret123'"),
            ("identity_access", "review_access_controls", "AllowAny admin action: *"),
            ("network_defense", "review_network_exposure", "bind 0.0.0.0 and verify=false"),
            ("supply_chain_security", "review_supply_chain", "curl https://example.test/install.sh | sh"),
        )

        for agent_name, action, text in cases:
            with self.subTest(agent=agent_name):
                agent = registry.get(agent_name)
                self.assertIsNotNone(agent)

                result = agent.execute(AgentCommand(action=action, payload={"text": text}))

                self.assertTrue(result.success)
                self.assertGreaterEqual(len(result.data["work_product"]["findings"]), 1)

    def test_active_red_team_simulation_requires_authorization_object(self) -> None:
        registry = build_default_registry()
        agent = registry.get("red_team_simulator")
        self.assertIsNotNone(agent)

        result = agent.execute(AgentCommand(action="simulate_lab_adversary", payload={"target": "lab-web"}))

        self.assertFalse(result.success)
        self.assertEqual(result.data["policy_decision"], "deny")

    def test_dispatcher_requires_t3_scope_and_confirmation_for_lab_simulation(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        agent = [item for item in build_default_agents() if item.name == "red_team_simulator"][0]
        dispatcher.register_agent(agent)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        authorization = {
            "owner": "local-owner",
            "scope_type": "local_lab",
            "targets": ["lab-web"],
            "allowed_actions": ["simulate_lab_adversary"],
            "forbidden_actions": [
                "external_targeting",
                "persistence",
                "credential_theft",
                "malware_deployment",
                "evasion",
                "exfiltration",
            ],
        }
        session = dispatcher.permission_engine.create_scoped_session(
            allowed_agents=("red_team_simulator",),
            allowed_tiers=(PermissionTier.T3,),
            scope_grants=(ScopeGrant("cyber.authorized_scope"),),
        )
        payload = {
            "target": "lab-web",
            "authorization": authorization,
            "scoped_session_id": session.id,
            "confirmed": True,
            "confirmation_expires_at": expires_at,
        }
        payload["confirmation_action_hash"] = action_tuple_hash(
            agent="red_team_simulator",
            capability="simulate_lab_adversary",
            action="simulate_lab_adversary",
            target="lab-web",
            parameters=payload,
            session=session.id,
            expires_at=expires_at,
        )

        blocked = dispatcher.dispatch(
            Task(
                description="Missing scope",
                action="simulate_lab_adversary",
                target_agent="red_team_simulator",
                payload={"target": "lab-web", "authorization": authorization},
            ),
            plan_id="plan-1",
        )
        allowed = dispatcher.dispatch(
            Task(
                description="Approved lab simulation",
                action="simulate_lab_adversary",
                target_agent="red_team_simulator",
                payload=payload,
            ),
            plan_id="plan-1",
        )

        self.assertFalse(blocked.success)
        self.assertEqual(blocked.data["decision"], "scope_violation")
        self.assertTrue(allowed.success)
        self.assertTrue(allowed.data["isolated"])


if __name__ == "__main__":
    unittest.main()
