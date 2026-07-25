import tempfile
import unittest
from pathlib import Path

from core.config import AppConfig
from core.startup import bootstrap


def make_runtime():
    temp_dir = tempfile.TemporaryDirectory()
    root = Path(temp_dir.name)
    runtime = bootstrap(
        AppConfig(
            environment="test",
            data_dir=root / "data",
            plugin_dir=root / "plugins",
            enable_voice=False,
            voice_auto_speak_responses=False,
        )
    )
    return runtime, temp_dir


class ConversationQATests(unittest.TestCase):
    def test_identity_question_answers_without_plan(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("מי את?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "IdentityQuestion")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"[\u0590-\u05ff]")
        self.assertIn("נלה", response)

    def test_agent_status_question_mentions_connected_agents(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("איזה סוכנים מחוברים?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "AgentStatusQuestion")
        self.assertIsNone(turn.plan)
        self.assertIn("סוכנים", response)
        self.assertIn("agent_count", turn.intent.parameters["response_variables"])

    def test_unknown_question_gets_honest_boundary_response(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("מה קורה בירח?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "GeneralQuestion")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"[\u0590-\u05ff]")


if __name__ == "__main__":
    unittest.main()
