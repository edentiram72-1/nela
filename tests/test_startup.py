import tempfile
import unittest
from pathlib import Path

from core.config import AppConfig
from core.startup import bootstrap


class StartupTests(unittest.TestCase):
    def test_bootstrap_returns_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = bootstrap(
                AppConfig(
                    environment="test",
                    log_level="INFO",
                    data_dir=root / "data",
                    plugin_dir=root / "plugins",
                    enable_voice=False,
                    enable_vision=False,
                )
            )

            turn = runtime.conversation.handle_text("Open Spotify and play relaxing music")

        self.assertEqual(runtime.config.environment, "test")
        self.assertEqual(turn.intent.action, "PlayMedia")
        self.assertEqual(len(turn.plan.tasks), 4)
        self.assertIn("spotify", runtime.dispatcher.discover_agents())
        self.assertIn("voice", runtime.dispatcher.discover_agents())
        self.assertIn("memory", runtime.dispatcher.discover_agents())
        self.assertIn("claude", runtime.dispatcher.discover_agents())
        self.assertIn("secure_code_reviewer", runtime.dispatcher.discover_agents())
        self.assertIn("orchestrator", runtime.dispatcher.discover_agents())
        self.assertIn("test_qa", runtime.dispatcher.discover_agents())


if __name__ == "__main__":
    unittest.main()
