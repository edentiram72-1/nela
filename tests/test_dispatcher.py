import unittest
import time

from agents.base import AgentCommand, AgentResult, BaseAgent
from agents.registry import DuplicateAgentError
from brain.dispatcher import AgentDispatcher
from brain.planner import RetryPolicy, Task
from core.events import EventBus, EventTypes
from permissions import AgentManifest, Capability, PermissionTier, action_tuple_hash
from datetime import datetime, timedelta, timezone
import os
import threading


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


class PidAgent(BaseAgent):
    name = "pid"
    permission_manifest = AgentManifest(agent="pid", capabilities=(Capability("pid", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "pid", {"pid": os.getpid()})


class BlockingAgent(BaseAgent):
    name = "blocking"
    permission_manifest = AgentManifest(agent="blocking", capabilities=(Capability("block", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        time.sleep(float(command.payload.get("seconds", 5.0)))
        return AgentResult(True, "blocked then completed")


class IsolatedCrashAgent(BaseAgent):
    name = "isolated_crash"
    permission_manifest = AgentManifest(agent="isolated_crash", capabilities=(Capability("crash", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        raise RuntimeError("isolated boom")


class DesktopLikeAgent(BaseAgent):
    name = "desktop"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "desktop ok", {"action": command.action, "application": command.payload.get("application")})


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
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        payload = {"confirmed": True, "confirmation_expires_at": expires_at}
        payload["confirmation_action_hash"] = action_tuple_hash(
            agent="echo",
            capability="sensitive_echo",
            action="sensitive_echo",
            target=None,
            parameters=payload,
            expires_at=expires_at,
        )
        allowed = dispatcher.dispatch(
            Task(
                description="Sensitive echo",
                action="sensitive_echo",
                target_agent="echo",
                payload=payload,
            ),
            plan_id="plan-1",
        )

        self.assertFalse(blocked.success)
        self.assertEqual(blocked.data["decision"], "confirmation_required")
        self.assertTrue(allowed.success)
        self.assertTrue(allowed.data["isolated"])
        self.assertEqual(allowed.data["isolated_outcome"], "completed")
        self.assertIn(EventTypes.PERMISSION_REQUESTED, [event.type for event in events.history()])
        self.assertIn(EventTypes.PERMISSION_GRANTED, [event.type for event in events.history()])

    def test_duplicate_agent_registration_is_rejected(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        with self.assertRaises(DuplicateAgentError):
            dispatcher.register_agent(EchoAgent())

    def test_routes_by_capability_when_target_agent_is_not_hardcoded(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(DesktopLikeAgent())

        result = dispatcher.dispatch(
            Task(
                description="Open Spotify",
                action="launch_application",
                capability="desktop.application.launch",
                payload={"application": "Spotify"},
            ),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        dispatched = [event for event in events.history() if event.type == EventTypes.TASK_DISPATCHED]
        self.assertEqual(dispatched[-1].payload["agent"], "desktop")
        self.assertEqual(dispatched[-1].payload["capability"], "desktop.application.launch")

    def test_explicitly_isolated_agent_runs_in_child_process(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(PidAgent())

        result = dispatcher.dispatch(
            Task(
                description="Isolated pid",
                action="pid",
                target_agent="pid",
                payload={"requires_isolation": True},
            ),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        self.assertTrue(result.data["isolated"])
        self.assertNotEqual(result.data["pid"], os.getpid())
        self.assertEqual(dispatcher.active_workers(), ())

    def test_safe_low_risk_agent_runs_without_isolation(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(PidAgent())

        result = dispatcher.dispatch(
            Task(description="Local pid", action="pid", target_agent="pid"),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data["pid"], os.getpid())
        self.assertNotIn("isolated", result.data)

    def test_kill_switch_terminates_blocked_isolated_worker_and_denies_new_dispatch(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(BlockingAgent())
        dispatcher.permission_engine.create_scoped_session(reason="revoked by kill switch test")
        task = Task(
            description="Blocked worker",
            action="block",
            target_agent="blocking",
            payload={"requires_isolation": True, "seconds": 5.0},
            timeout_seconds=5.0,
        )
        result_holder: dict[str, AgentResult] = {}

        thread = threading.Thread(
            target=lambda: result_holder.setdefault("result", dispatcher.dispatch(task, "plan-kill")),
            daemon=True,
        )
        thread.start()

        deadline = time.monotonic() + 2.0
        while not dispatcher.active_workers() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(dispatcher.active_workers())

        dispatcher.permission_engine.activate_kill_switch("unit test kill")
        thread.join(3.0)

        self.assertFalse(thread.is_alive())
        result = result_holder["result"]
        self.assertFalse(result.success)
        self.assertEqual(result.data["isolated_outcome"], "cancelled")
        self.assertEqual(dispatcher.active_workers(), ())
        self.assertEqual(dispatcher.permission_engine.scoped_sessions(), ())
        self.assertTrue(
            any(record.result_success is False and "cancelled" in (record.result_message or "") for record in dispatcher.permission_engine.audit_log.records())
        )

        denied = dispatcher.dispatch(
            Task(description="New blocked task", action="block", target_agent="blocking"),
            plan_id="plan-kill",
        )
        self.assertFalse(denied.success)
        self.assertEqual(denied.data["decision"], "kill_switch_active")

    def test_isolated_worker_crash_returns_structured_failure(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(IsolatedCrashAgent())

        result = dispatcher.dispatch(
            Task(
                description="Isolated crash",
                action="crash",
                target_agent="isolated_crash",
                payload={"requires_isolation": True},
            ),
            plan_id="plan-1",
        )

        self.assertFalse(result.success)
        self.assertEqual(result.data["isolated_outcome"], "failed")
        self.assertEqual(result.data["error_type"], "RuntimeError")


if __name__ == "__main__":
    unittest.main()
