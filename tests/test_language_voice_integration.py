import tempfile
import unittest
from pathlib import Path

from agents.voice.agent import VoiceAgent
from core.config import AppConfig
from core.startup import bootstrap
from voice.providers.mock import MockSpeechProvider


class LanguageVoiceIntegrationTests(unittest.TestCase):
    def test_semantic_turn_renders_hebrew_and_delegates_to_voice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = bootstrap(
                AppConfig(
                    environment="test",
                    data_dir=root / "data",
                    plugin_dir=root / "plugins",
                    enable_voice=True,
                    voice_auto_speak_responses=True,
                    voice_silent_mode=False,
                )
            )
            provider = MockSpeechProvider()
            runtime.dispatcher.unregister_agent("voice")
            runtime.dispatcher.register_agent(VoiceAgent(events=runtime.events, provider=provider, enabled=True, silent=False))

            turn = runtime.conversation.handle_text("Open Spotify and play my Night playlist")
            text = runtime.response_adapter.render_and_maybe_speak(turn)

        self.assertRegex(text, r"[\u0590-\u05ff]")
        self.assertEqual(provider.spoken[0][0], text)


if __name__ == "__main__":
    unittest.main()
