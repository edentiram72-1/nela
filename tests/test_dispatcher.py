import unittest
import time

from agents.base import AgentCommand, AgentResult, BaseAgent
from brain.dispatcher import AgentDispatcher
from brain.planner import RetryPolicy, Task
from core.events import EventBus, EventTypes
from permissions import AgentManifest, Capability, PermissionTier


class EchoAgent(BaseAgent):
    name = "echo"
    permission_manifest = AgentManifest(
        agent="echo",
        capabilities=(
            Capability("echo", PermissionTier.T1),
            Capability("sensitive_echo", PermissionTier.T2, requires_confirmation=True),
        ),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "ok", {"action": command.action})


class SlowSuccessAgent(BaseAgent):
    name = "slow_success"
    permission_manifest = AgentManifest(agent="slow_success", capabilities=(Capability("run", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        time.sleep(0.01)
        return AgentResult(True, "slow ok")


class SlowFailureAgent(BaseAgent):
    name = "slow_failure"
    permission_manifest = AgentManifest(agent="slow_failure", capabilities=(Capability("run", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        time.sleep(0.01)
        return AgentResult(False, "slow failed")


class FlakyAgent(BaseAgent):
    name = "flaky"
    permission_manifest = AgentManifest(agent="flaky", capabilities=(Capability("run", PermissionTier.T1),))

    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def execute(self, command: AgentCommand) -> AgentResult:
        self.calls += 1
        if self.calls == 1:
            return AgentResult(False, "try again")
        return AgentResult(True, "ok after retry")


class CrashingAgent(BaseAgent):
    name = "crashing"
    permission_manifest = AgentManifest(agent="crashing", capabilities=(Capability("run", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        raise RuntimeError("boom")


class DispatcherTests(unittest.TestCase):
    def test_registers_discovers_and_dispatches_agent(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        result = dispatcher.dispatch(
            Task(
                description="Echo task",
                action="echo",
                target_agent="echo",
                retry_policy=RetryPolicy(max_attempts=1),
            ),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        self.assertEqual(dispatcher.discover_agents(), ("echo",))
        self.assertIn(EventTypes.TASK_COMPLETED, [event.type for event in events.history()])

    def test_reports_unavailable_agent(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)

        result = dispatcher.dispatch(
            Task(description="Missing task", action="run", target_agent="missing"),
            plan_id="plan-1",
        )

        self.assertFalse(result.success)
        self.assertIn(EventTypes.AGENT_UNAVAILABLE, [event.type for event in events.history()])

    def test_slow_success_is_not_rewritten_as_timeout_failure(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(SlowSuccessAgent())

        result = dispatcher.dispatch(
            Task(description="Slow success", action="run", target_agent="slow_success", timeout_seconds=0.001),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        self.assertTrue(result.data["timeout_exceeded"])
        self.assertIn(EventTypes.TASK_COMPLETED, [event.type for event in events.history()])

    def test_slow_failure_reports_timeout(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(SlowFailureAgent())

        result = dispatcher.dispatch(
            Task(description="Slow failure", action="run", target_agent="slow_failure", timeout_seconds=0.001),
            plan_id="plan-1",
        )

        self.assertFalse(result.success)
        self.assertEqual(result.message, "Task timed out.")
        self.assertIn(EventTypes.TASK_FAILED, [event.type for event in events.history()])

    def test_retry_can_succeed_after_first_failure(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        agent = FlakyAgent()
        dispatcher.register_agent(agent)

        result = dispatcher.dispatch(
            Task(
                description="Flaky task",
                action="run",
                target_agent="flaky",
                retry_policy=RetryPolicy(max_attempts=2),
            ),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        self.assertEqual(agent.calls, 2)
        self.assertIn(EventTypes.TASK_COMPLETED, [event.type for event in events.history()])

    def test_agent_exception_becomes_task_failure(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(CrashingAgent())

        result = dispatcher.dispatch(
            Task(description="Crash task", action="run", target_agent="crashing"),
            plan_id="plan-1",
        )

        self.assertFalse(result.success)
        self.assertIn("RuntimeError", result.message)
        self.assertIn(EventTypes.TASK_FAILED, [event.type for event in events.history()])

    def test_denies_action_missing_from_manifest_before_execution(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        result = dispatcher.dispatch(
            Task(
                description="Blocked task",
                action="unknown_echo",
                target_agent="echo",
                retry_policy=RetryPolicy(max_attempts=1),
            ),
            plan_id="plan-1",
        )

        event_types = [event.type for event in events.history()]
        self.assertFalse(result.success)
        self.assertEqual(result.data["tier"], PermissionTier.T4.value)
        self.assertIn(EventTypes.PERMISSION_DENIED, event_types)
        self.assertNotIn(EventTypes.TASK_STARTED, event_types)

    def test_t2_action_requires_confirmation_payload(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        blocked = dispatcher.dispatch(
            Task(description="Sensitive echo", action="sensitive_echo", target_agent="echo"),
            plan_id="plan-1",
        )
        allowed = dispatcher.dispatch(
            Task(
                description="Sensitive echo",
                action="sensitive_echo",
                target_agent="echo",
                payload={"confirmed": True},
            ),
            plan_id="plan-1",
        )

        self.assertFalse(blocked.success)
        self.assertEqual(blocked.data["decision"], "confirmation_required")
        self.assertTrue(allowed.success)
        self.assertIn(EventTypes.PERMISSION_REQUESTED, [event.type for event in events.history()])
        self.assertIn(EventTypes.PERMISSION_GRANTED, [event.type for event in events.history()])


if __name__ == "__main__":
    unittest.main()
