import unittest

from brain.context import ContextEngine


class ContextEngineTests(unittest.TestCase):
    def test_tracks_conversation_and_running_tasks(self) -> None:
        context = ContextEngine()
        turn_id = context.start_turn("Open Spotify")
        context.record_intent("OpenApplication")
        context.mark_task_running("task-1", "Launch app", "spotify")

        snapshot = context.snapshot()

        self.assertEqual(snapshot.current_turn_id, turn_id)
        self.assertEqual(snapshot.last_intent, "OpenApplication")
        self.assertIn("task-1", snapshot.running_tasks)

        context.mark_task_finished("task-1")
        self.assertNotIn("task-1", context.snapshot().running_tasks)


if __name__ == "__main__":
    unittest.main()

