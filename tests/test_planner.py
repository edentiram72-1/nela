import unittest

from brain.intent_router import IntentRouter
from brain.planner import Planner, TaskMode


class PlannerTests(unittest.TestCase):
    def test_planner_breaks_media_request_into_sequential_tasks(self) -> None:
        intent = IntentRouter().classify("Open Spotify and play my Night playlist")
        plan = Planner().create_plan(intent)

        self.assertEqual([task.action for task in plan.tasks], [
            "ensure_application",
            "wait_until_ready",
            "search_media",
            "play_media",
        ])
        self.assertTrue(all(task.mode == TaskMode.SEQUENTIAL for task in plan.tasks))
        self.assertEqual(plan.tasks[1].depends_on, (plan.tasks[0].id,))
        self.assertEqual(plan.tasks[2].depends_on, (plan.tasks[1].id,))
        self.assertEqual(plan.tasks[3].depends_on, (plan.tasks[2].id,))

    def test_planner_adds_retries_and_timeouts(self) -> None:
        intent = IntentRouter().classify("Open Spotify")
        plan = Planner().create_plan(intent)

        self.assertEqual(plan.tasks[0].target_agent, "desktop")
        self.assertEqual(plan.tasks[0].retry_policy.max_attempts, 2)
        self.assertEqual(plan.tasks[0].timeout_seconds, 20.0)

    def test_planner_routes_close_application_to_desktop(self) -> None:
        intent = IntentRouter().classify("close Finder")
        plan = Planner().create_plan(intent)

        self.assertEqual(plan.tasks[0].action, "close_application")
        self.assertEqual(plan.tasks[0].target_agent, "desktop")
        self.assertEqual(plan.tasks[0].payload["application"], "Finder")

    def test_planner_routes_switch_application_to_desktop(self) -> None:
        intent = IntentRouter().classify("switch to Spotify")
        plan = Planner().create_plan(intent)

        self.assertEqual(plan.tasks[0].action, "switch_application")
        self.assertEqual(plan.tasks[0].target_agent, "desktop")
        self.assertEqual(plan.tasks[0].payload["application"], "Spotify")

    def test_planner_can_cancel_plan(self) -> None:
        intent = IntentRouter().classify("Open Spotify")
        plan = Planner().create_plan(intent)
        cancelled = Planner().cancel_plan(plan)

        self.assertTrue(all(task.status.value == "cancelled" for task in cancelled.tasks))


if __name__ == "__main__":
    unittest.main()
