import unittest
import time
import threading

from agents.base import AgentCommand, AgentResult, BaseAgent
from agents.process_isolation import ProcessOutcome
from agents.registry import AgentNotRegisteredError, AgentRegistry, DuplicateAgentError
from brain.dispatcher import AgentDispatcher
from brain.planner import RetryPolicy, Task
from core.events import EventBus, EventTypes
from permissions import AgentManifest, Capability, PermissionEngine, PermissionTier, action_tuple_hash
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile


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


class DesktopLikeAgent(BaseAgent):
    name = "desktop"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "desktop ok", {"action": command.action, "application": command.payload.get("application")})


class BlockingSensitiveAgent(BaseAgent):
    name = "blocking_sensitive"
    permission_manifest = AgentManifest(
        agent="blocking_sensitive",
        capabilities=(Capability("sensitive_wait", PermissionTier.T2, requires_confirmation=True),),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        marker_path = command.payload.get("marker_path")
        if marker_path:
            with Path(str(marker_path)).open("a", encoding="utf-8") as marker:
                marker.write("started\n")
        time.sleep(float(command.payload.get("sleep_seconds", 5.0)))
        return AgentResult(True, "finished")


class KillAfterAuthorizePermissionEngine(PermissionEngine):
    def __init__(self, events: EventBus) -> None:
        super().__init__(events=events)
        self.triggered = False

    def authorize(self, request):
        result = super().authorize(request)
        if result.granted and not self.triggered:
            self.triggered = True
            self.activate_kill_switch("post authorization race")
        return result


class KillOnRunnerRegistrationPermissionEngine(PermissionEngine):
    def __init__(self, events: EventBus) -> None:
        super().__init__(events=events)
        self.triggered = False

    def register_isolated_runner(self, runner) -> str:
        token = super().register_isolated_runner(runner)
        if not self.triggered:
            self.triggered = True
            self.activate_kill_switch("runner registration race")
        return token


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
        self.assertIn(EventTypes.PERMISSION_REQUESTED, [event.type for event in events.history()])
        self.assertIn(EventTypes.PERMISSION_GRANTED, [event.type for event in events.history()])

    def test_duplicate_agent_registration_is_rejected(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        with self.assertRaises(DuplicateAgentError):
            dispatcher.register_agent(EchoAgent())

    def test_agent_replace_rejects_missing_agent(self) -> None:
        registry = AgentRegistry()

        with self.assertRaises(AgentNotRegisteredError):
            registry.replace(EchoAgent())

        self.assertEqual(registry.registration_audit[-1], {"agent": "echo", "result": "rejected_missing"})
        self.assertEqual(registry.names(), ())

    def test_agent_replace_requires_existing_agent(self) -> None:
        registry = AgentRegistry()
        registry.register(EchoAgent())
        replacement = EchoAgent()

        registry.replace(replacement)

        self.assertIs(registry.get("echo"), replacement)
        self.assertEqual(registry.registration_audit[-1], {"agent": "echo", "result": "replaced"})

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

    def test_kill_switch_terminates_inflight_isolated_task(self) -> None:
        events = EventBus()
        permission_engine = PermissionEngine(events=events)
        dispatcher = AgentDispatcher(events, permission_engine=permission_engine)
        dispatcher.register_agent(BlockingSensitiveAgent())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        payload = {"confirmed": True, "confirmation_expires_at": expires_at, "sleep_seconds": 5.0}
        payload["confirmation_action_hash"] = action_tuple_hash(
            agent="blocking_sensitive",
            capability="sensitive_wait",
            action="sensitive_wait",
            target=None,
            parameters=payload,
            expires_at=expires_at,
        )
        result_holder: list[AgentResult] = []
        task = Task(
            description="Blocking sensitive task",
            action="sensitive_wait",
            target_agent="blocking_sensitive",
            payload=payload,
            timeout_seconds=10.0,
        )
        worker = threading.Thread(target=lambda: result_holder.append(dispatcher.dispatch(task, plan_id="plan-1")))

        worker.start()
        deadline = time.monotonic() + 3.0
        while permission_engine.active_isolated_runner_count() == 0 and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertEqual(permission_engine.active_isolated_runner_count(), 1)

        permission_engine.activate_kill_switch("unit test")
        worker.join(3.0)

        self.assertFalse(worker.is_alive())
        self.assertEqual(permission_engine.active_isolated_runner_count(), 0)
        self.assertEqual(len(result_holder), 1)
        self.assertFalse(result_holder[0].success)
        self.assertEqual(result_holder[0].data["isolated_outcome"], ProcessOutcome.TERMINATED.value)
        kill_events = [event for event in events.history() if event.type == EventTypes.KILL_SWITCH_ACTIVATED]
        self.assertEqual(kill_events[-1].payload["terminated_processes"], 1)

    def test_kill_switch_blocks_retry_after_isolated_termination(self) -> None:
        events = EventBus()
        permission_engine = PermissionEngine(events=events)
        dispatcher = AgentDispatcher(events, permission_engine=permission_engine)
        dispatcher.register_agent(BlockingSensitiveAgent())
        with tempfile.TemporaryDirectory() as directory:
            marker_path = Path(directory) / "attempts.txt"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            payload = {
                "confirmed": True,
                "confirmation_expires_at": expires_at,
                "marker_path": str(marker_path),
                "sleep_seconds": 1.0,
            }
            payload["confirmation_action_hash"] = action_tuple_hash(
                agent="blocking_sensitive",
                capability="sensitive_wait",
                action="sensitive_wait",
                target=None,
                parameters=payload,
                expires_at=expires_at,
            )
            result_holder: list[AgentResult] = []
            task = Task(
                description="Blocking sensitive retry task",
                action="sensitive_wait",
                target_agent="blocking_sensitive",
                payload=payload,
                timeout_seconds=3.0,
                retry_policy=RetryPolicy(max_attempts=2),
            )
            worker = threading.Thread(target=lambda: result_holder.append(dispatcher.dispatch(task, plan_id="plan-1")))

            worker.start()
            deadline = time.monotonic() + 3.0
            while not marker_path.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(marker_path.exists())
            permission_engine.activate_kill_switch("unit test")
            worker.join(3.0)

            self.assertFalse(worker.is_alive())
            self.assertEqual(len(result_holder), 1)
            self.assertFalse(result_holder[0].success)
            self.assertTrue(result_holder[0].data["kill_switch_active"])
            self.assertTrue(result_holder[0].data["retry_blocked"])
            self.assertEqual(marker_path.read_text(encoding="utf-8").splitlines(), ["started"])

    def test_kill_switch_after_authorization_blocks_first_attempt(self) -> None:
        events = EventBus()
        permission_engine = KillAfterAuthorizePermissionEngine(events=events)
        dispatcher = AgentDispatcher(events, permission_engine=permission_engine)
        dispatcher.register_agent(BlockingSensitiveAgent())
        with tempfile.TemporaryDirectory() as directory:
            marker_path = Path(directory) / "attempts.txt"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            payload = {
                "confirmed": True,
                "confirmation_expires_at": expires_at,
                "marker_path": str(marker_path),
                "sleep_seconds": 0.1,
            }
            payload["confirmation_action_hash"] = action_tuple_hash(
                agent="blocking_sensitive",
                capability="sensitive_wait",
                action="sensitive_wait",
                target=None,
                parameters=payload,
                expires_at=expires_at,
            )

            result = dispatcher.dispatch(
                Task(
                    description="Post-authorization kill switch race",
                    action="sensitive_wait",
                    target_agent="blocking_sensitive",
                    payload=payload,
                    timeout_seconds=3.0,
                    retry_policy=RetryPolicy(max_attempts=1),
                ),
                plan_id="plan-1",
            )

            self.assertFalse(result.success)
            self.assertTrue(result.data["kill_switch_active"])
            self.assertFalse(marker_path.exists())

    def test_kill_switch_during_runner_registration_blocks_process_start(self) -> None:
        events = EventBus()
        permission_engine = KillOnRunnerRegistrationPermissionEngine(events=events)
        dispatcher = AgentDispatcher(events, permission_engine=permission_engine)
        dispatcher.register_agent(BlockingSensitiveAgent())
        with tempfile.TemporaryDirectory() as directory:
            marker_path = Path(directory) / "attempts.txt"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            payload = {
                "confirmed": True,
                "confirmation_expires_at": expires_at,
                "marker_path": str(marker_path),
                "sleep_seconds": 0.1,
            }
            payload["confirmation_action_hash"] = action_tuple_hash(
                agent="blocking_sensitive",
                capability="sensitive_wait",
                action="sensitive_wait",
                target=None,
                parameters=payload,
                expires_at=expires_at,
            )

            result = dispatcher.dispatch(
                Task(
                    description="Runner registration kill switch race",
                    action="sensitive_wait",
                    target_agent="blocking_sensitive",
                    payload=payload,
                    timeout_seconds=3.0,
                    retry_policy=RetryPolicy(max_attempts=1),
                ),
                plan_id="plan-1",
            )

            self.assertFalse(result.success)
            self.assertTrue(result.data["kill_switch_active"])
            self.assertFalse(marker_path.exists())


if __name__ == "__main__":
    unittest.main()
