import tempfile
import unittest
from pathlib import Path

from agents.base import AgentCommand
from agents.tryhackme import TryHackMeLearningAgent
from memory.learning_core import LearningMemoryStore


class TryHackMeLearningTests(unittest.TestCase):
    def test_capture_lesson_persists_structured_learning_memory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lessons.json"
            store = LearningMemoryStore(path)
            agent = TryHackMeLearningAgent(store=store)

            result = agent.execute(
                AgentCommand(
                    action="capture_tryhackme_lesson",
                    payload={
                        "room": "Nmap",
                        "text": "TryHackMe room Nmap: nmap -sV 10.10.10.10 finds ports and services.",
                    },
                )
            )

            reloaded = LearningMemoryStore(path)
            lessons = reloaded.list_lessons(source="tryhackme")

        self.assertTrue(result.success)
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].room, "Nmap")
        self.assertIn("nmap", lessons[0].concepts)
        self.assertTrue(any("nmap -sV" in command for command in lessons[0].commands))
        steps = result.data["work_product"]["steps"]
        self.assertTrue(any("זיהיתי נושא" in step for step in steps))
        self.assertTrue(any("שמרתי" in step for step in steps))

    def test_progress_review_reports_empty_and_populated_state(self) -> None:
        store = LearningMemoryStore()
        agent = TryHackMeLearningAgent(store=store)

        empty = agent.execute(AgentCommand(action="review_tryhackme_progress", payload={}))
        captured = agent.execute(
            AgentCommand(
                action="capture_tryhackme_lesson",
                payload={"text": "TryHackMe Linux room: learned permissions and ssh basics."},
            )
        )
        progress = agent.execute(AgentCommand(action="review_tryhackme_progress", payload={}))

        self.assertTrue(empty.success)
        self.assertIn("עוד אין", empty.data["work_product"]["findings"][0]["title"])
        self.assertTrue(captured.success)
        self.assertTrue(progress.success)
        self.assertIn("steps", progress.data["work_product"])
        self.assertIn("שיעורי TryHackMe", progress.data["work_product"]["findings"][0]["title"])


if __name__ == "__main__":
    unittest.main()
