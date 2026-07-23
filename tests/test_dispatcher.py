import unittest
import time

from agents.base import AgentCommand, AgentResult, BaseAgent
from brain.dispatcher import AgentDispatcher
from brain.planner import RetryPolicy, Task
from core.events import EventBus, EventTypes


class EchoAgent(BaseAgent):
    name = "echo"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "ok", {"action": command.action})


class SlowSuccessAgent(BaseAgent):
    name = "slow_success"

    def execute(self, command: AgentCommand) -> AgentResult:
        time.sleep(0.01)
        return AgentResult(True, "slow ok")


class SlowFailureAgent(BaseAgent):
    name = "slow_failure"

    def execute(self, command: AgentCommand) -> AgentResult:
        time.sleep(0.01)
        return AgentResult(False, "slow failed")


class FlakyAgent(BaseAgent):
    name = "flaky"

    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def execute(self, command: AgentCommand) -> AgentResult:
        self.calls += 1
        if self.calls == 1:
            return AgentResult(False, "try again")
        return AgentResult(True, "ok after retry")


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


if __name__ == "__main__":
    unittest.main()
