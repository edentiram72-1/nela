from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from agents.base import AgentCommand
from agents.factory import build_default_agents, build_default_registry
from brain.dispatcher import AgentDispatcher
from brain.planner import Task
from core.events import EventBus
from permissions import action_tuple_hash


AUTOMATION_AGENT_NAMES = {
    "automation",
    "automation_workflow",
    "computer_control",
    "app_automation",
    "file_automation",
    "process_automation",
    "scheduler_automation",
}


class ComputerAutomationAgentTests(unittest.TestCase):
    def test_registry_contains_computer_automation_agents(self) -> None:
        registry = build_default_registry()

        self.assertTrue(AUTOMATION_AGENT_NAMES.issubset(set(registry.names())))

    def test_automation_coordinator_routes_to_specialists(self) -> None:
        registry = build_default_registry()
        automation = registry.get("automation")
        self.assertIsNotNone(automation)

        result = automation.execute(AgentCommand(action="route_computer_task", payload={"task_type": "process"}))

        self.assertTrue(result.success)
        artifacts = result.data["work_product"]["artifacts"]
        self.assertIn("target_agent=process_automation", artifacts[0]["content"])

    def test_ui_and_file_agents_are_preview_only(self) -> None:
        registry = build_default_registry()
        control = registry.get("computer_control")
        files = registry.get("file_automation")
        self.assertIsNotNone(control)
        self.assertIsNotNone(files)

        ui_result = control.execute(
            AgentCommand(action="plan_ui_sequence", payload={"application": "Finder", "actions": ["focus", "inspect"]})
        )
        file_result = files.execute(
            AgentCommand(action="preview_file_operation", payload={"operation": "move", "paths": ["../secret.txt"]})
        )

        self.assertTrue(ui_result.success)
        self.assertEqual(ui_result.data["work_product"]["steps"], ["focus", "inspect"])
        self.assertTrue(file_result.success)
        self.assertEqual(file_result.data["work_product"]["findings"][0]["severity"], "high")

    def test_process_agent_dry_run_and_blocked_command(self) -> None:
        registry = build_default_registry()
        process = registry.get("process_automation")
        self.assertIsNotNone(process)

        dry_run = process.execute(
            AgentCommand(
                action="run_allowlisted_command",
                payload={"command": ["git", "status", "--short", "--branch"]},
            )
        )
        blocked = process.execute(
            AgentCommand(
                action="run_allowlisted_command",
                payload={"command": ["rm", "-rf", "/tmp/demo"]},
            )
        )

        self.assertTrue(dry_run.success)
        self.assertIn("Dry-run", dry_run.data["work_product"]["summary"])
        self.assertTrue(blocked.success)
        self.assertIn("blocked", blocked.data["work_product"]["summary"])
        self.assertEqual(blocked.data["work_product"]["findings"][0]["severity"], "high")

    def test_process_execution_requires_dispatcher_confirmation(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        process = [agent for agent in build_default_agents() if agent.name == "process_automation"][0]
        dispatcher.register_agent(process)
        payload = {
            "command": ["git", "status", "--short", "--branch"],
            "dry_run": False,
            "approved": True,
        }

        blocked = dispatcher.dispatch(
            Task(
                description="Run allowlisted command without confirmation",
                action="run_allowlisted_command",
                target_agent="process_automation",
                payload=payload,
            ),
            plan_id="plan-automation",
        )

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        confirmed_payload = {**payload, "confirmed": True, "confirmation_expires_at": expires_at}
        confirmed_payload["confirmation_action_hash"] = action_tuple_hash(
            agent="process_automation",
            capability="run_allowlisted_command",
            action="run_allowlisted_command",
            target=None,
            parameters=confirmed_payload,
            expires_at=expires_at,
        )
        allowed = dispatcher.dispatch(
            Task(
                description="Run allowlisted command with confirmation",
                action="run_allowlisted_command",
                target_agent="process_automation",
                payload=confirmed_payload,
            ),
            plan_id="plan-automation",
        )

        self.assertFalse(blocked.success)
        self.assertEqual(blocked.data["decision"], "confirmation_required")
        self.assertTrue(allowed.success)
        self.assertTrue(allowed.data["isolated"])
        self.assertIn("exit code 0", allowed.message)


if __name__ == "__main__":
    unittest.main()
