import tempfile
import unittest
from pathlib import Path

from agents.base import AgentCommand, AgentResult, BaseAgent
from agents.voice.agent import VoiceAgent
from core.config import AppConfig
from core.startup import bootstrap
from nela_runtime.server import NelaDemoController, render_eye_html, render_index_html
from voice.providers.mock import MockSpeechProvider


class MockDesktopAgent(BaseAgent):
    name = "desktop"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(
            True,
            "Spotify brought to foreground.",
            {"agent": "desktop", "application": command.payload.get("application")},
        )


class VerticalSliceDemoTests(unittest.TestCase):
    def test_hebrew_spotify_flow_reaches_voice_and_idle_eye_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = bootstrap(
                AppConfig(
                    environment="test",
                    data_dir=Path(temp_dir) / "data",
                    plugin_dir=Path(temp_dir) / "plugins",
                    enable_voice=True,
                    voice_auto_speak_responses=True,
                    voice_silent_mode=False,
                    voice_provider="mock",
                )
            )
            provider = MockSpeechProvider()
            runtime.dispatcher.unregister_agent("desktop")
            runtime.dispatcher.register_agent(MockDesktopAgent())
            runtime.dispatcher.unregister_agent("voice")
            runtime.dispatcher.register_agent(VoiceAgent(events=runtime.events, provider=provider, enabled=True, silent=False))

            controller = NelaDemoController(runtime)
            result = controller.process_message("נלה, תפתחי את Spotify")

        self.assertEqual(result["intent"], "OpenApplication")
        self.assertEqual(result["application"], "Spotify")
        self.assertRegex(result["response"], r"[\u0590-\u05ff]")
        self.assertTrue(provider.spoken)
        self.assertEqual(provider.spoken[0][0], result["response"])
        self.assertEqual(result["final_eye_state"], "idle")
        self.assertFalse(result["voice_output_active"])
        for expected_state in ("thinking", "executing", "success", "speaking", "idle"):
            self.assertIn(expected_state, result["eye_states"])

    def test_rendered_demo_hosts_living_eye_without_static_rewrite(self) -> None:
        page = render_index_html()
        eye = render_eye_html()

        self.assertIn('src="/eye"', page)
        self.assertIn("nela:set-state", page)
        self.assertIn("nela:set-state", eye)
        self.assertIn("<svg", eye)
        self.assertIn('data-state="idle"', eye)


if __name__ == "__main__":
    unittest.main()
