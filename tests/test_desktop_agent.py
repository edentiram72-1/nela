from __future__ import annotations

import subprocess
import unittest

from agents.base import AgentCommand, AgentState
from agents.desktop.agent import DesktopAgent


class FakeDesktopRunner:
    def __init__(
        self,
        running_processes: set[str] | None = None,
        open_returncode: int = 0,
        quit_returncode: int = 0,
    ) -> None:
        self.running_processes = running_processes or set()
        self.open_returncode = open_returncode
        self.quit_returncode = quit_returncode
        self.calls: list[tuple[str, ...]] = []

    def run(self, argv: tuple[str, ...], timeout: float) -> subprocess.CompletedProcess[str]:
        self.calls.append(argv)
        if argv[:2] == ("/usr/bin/pgrep", "-x"):
            process_name = argv[2]
            return subprocess.CompletedProcess(argv, 0 if process_name in self.running_processes else 1, "", "")
        if argv[:2] == ("/usr/bin/open", "-b"):
            return subprocess.CompletedProcess(argv, self.open_returncode, "", "open failed")
        if argv[:2] == ("/usr/bin/osascript", "-e"):
            return subprocess.CompletedProcess(argv, self.quit_returncode, "", "quit failed")
        return subprocess.CompletedProcess(argv, 99, "", "unexpected command")


class TimeoutDesktopRunner(FakeDesktopRunner):
    def run(self, argv: tuple[str, ...], timeout: float) -> subprocess.CompletedProcess[str]:
        self.calls.append(argv)
        raise subprocess.TimeoutExpired(argv, timeout)


class DesktopAgentTests(unittest.TestCase):
    def test_launch_existing_supported_app(self) -> None:
        runner = FakeDesktopRunner()
        agent = DesktopAgent(runner=runner)

        result = agent.execute(AgentCommand(action="launch_application", payload={"application": "Chrome"}))

        self.assertTrue(result.success)
        self.assertEqual(result.data["status"], "success")
        self.assertEqual(result.data["application"], "Google Chrome")
        self.assertEqual(result.data["action"], "launch")
        self.assertIn(("/usr/bin/open", "-b", "com.google.Chrome"), runner.calls)

    def test_launch_missing_app_fails_safely(self) -> None:
        runner = FakeDesktopRunner()
        agent = DesktopAgent(runner=runner)

        result = agent.execute(AgentCommand(action="launch_application", payload={"application": "Unknown App"}))

        self.assertFalse(result.success)
        self.assertEqual(result.data["status"], "failed")
        self.assertEqual(result.data["application"], "Unknown App")
        self.assertEqual(runner.calls, [])

    def test_detect_running_app(self) -> None:
        agent = DesktopAgent(runner=FakeDesktopRunner(running_processes={"Safari"}))

        result = agent.execute(AgentCommand(action="is_application_running", payload={"application": "Safari"}))

        self.assertTrue(result.success)
        self.assertTrue(result.data["running"])
        self.assertEqual(result.data["application"], "Safari")

    def test_bring_running_app_to_foreground(self) -> None:
        runner = FakeDesktopRunner(running_processes={"Safari"})
        agent = DesktopAgent(runner=runner)

        result = agent.execute(AgentCommand(action="switch_application", payload={"application": "Safari"}))

        self.assertTrue(result.success)
        self.assertEqual(result.data["action"], "bring_to_front")
        self.assertIn(("/usr/bin/open", "-b", "com.apple.Safari"), runner.calls)

    def test_close_running_app(self) -> None:
        runner = FakeDesktopRunner(running_processes={"Safari"})
        agent = DesktopAgent(runner=runner)

        result = agent.execute(AgentCommand(action="close_application", payload={"application": "Safari"}))

        self.assertTrue(result.success)
        self.assertEqual(result.data["action"], "close")
        self.assertIn(("/usr/bin/osascript", "-e", 'tell application id "com.apple.Safari" to quit'), runner.calls)

    def test_close_non_running_app_is_safe_success(self) -> None:
        runner = FakeDesktopRunner()
        agent = DesktopAgent(runner=runner)

        result = agent.execute(AgentCommand(action="close_application", payload={"application": "Safari"}))

        self.assertTrue(result.success)
        self.assertTrue(result.data["already_closed"])
        self.assertNotIn(
            ("/usr/bin/osascript", "-e", 'tell application id "com.apple.Safari" to quit'),
            runner.calls,
        )

    def test_wait_until_ready_reports_running_app(self) -> None:
        runner = FakeDesktopRunner(running_processes={"Safari"})
        agent = DesktopAgent(runner=runner)

        result = agent.execute(
            AgentCommand(action="wait_until_ready", payload={"application": "Safari", "timeout_seconds": 1})
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data["action"], "wait_until_ready")
        self.assertTrue(result.data["running"])

    def test_timeout_expired_returns_structured_failure(self) -> None:
        runner = TimeoutDesktopRunner()
        agent = DesktopAgent(runner=runner)

        result = agent.execute(AgentCommand(action="launch_application", payload={"application": "Safari"}))

        self.assertFalse(result.success)
        self.assertEqual(result.data["error"], "TimeoutExpired")
        self.assertEqual(result.data["action"], "launch_application")

    def test_spotify_launch_is_disabled(self) -> None:
        runner = FakeDesktopRunner()
        agent = DesktopAgent(runner=runner)

        result = agent.execute(AgentCommand(action="launch_application", payload={"application": "Spotify"}))

        self.assertFalse(result.success)
        self.assertEqual(result.data["status"], "failed")
        self.assertTrue(result.data["disabled_application"])
        self.assertIn("כבויה", result.message)
        self.assertNotIn("Spotify", result.data["supported_applications"])
        self.assertEqual(runner.calls, [])

    def test_lifecycle_and_health_check(self) -> None:
        agent = DesktopAgent(runner=FakeDesktopRunner())

        self.assertEqual(agent.status(), AgentState.CREATED)
        self.assertTrue(agent.initialize().success)
        self.assertEqual(agent.status(), AgentState.READY)

        health = agent.health_check()

        self.assertTrue(health.success)
        self.assertIn("Google Chrome", health.data["supported_applications"])
        self.assertEqual(health.data["safety"], "application_lifecycle_only")
        self.assertTrue(agent.stop().success)
        self.assertEqual(agent.status(), AgentState.STOPPED)


if __name__ == "__main__":
    unittest.main()
