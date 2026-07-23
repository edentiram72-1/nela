import tempfile
import unittest
from pathlib import Path

from core.config import AppConfig
from core.startup import bootstrap
from ui.router import UIRouter
from ui.state import MessageRole, UIStateManager


class UIRouterTests(unittest.TestCase):
    def test_submit_text_reaches_brain_and_records_chat_messages(self) -> None:
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
            state = UIStateManager()
            router = UIRouter(runtime=runtime, state=state)

            turn = router.submit_text("Open Spotify and play my Night playlist")

        self.assertEqual(turn.intent.action, "PlayMedia")
        self.assertEqual(state.state.messages[0].role, MessageRole.USER)
        self.assertEqual(state.state.messages[1].role, MessageRole.ASSISTANT)
        self.assertRegex(state.state.messages[1].content, r"[\u0590-\u05ff]")
        self.assertFalse(state.state.typing_indicator)

    def test_streaming_response_hooks_update_assistant_message(self) -> None:
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
            state = UIStateManager()
            router = UIRouter(runtime=runtime, state=state)

            message_id = router.start_streaming_response()
            router.append_streaming_response(message_id, "hello")
            router.finish_streaming_response(message_id)

        self.assertEqual(state.state.messages[0].content, "hello")
        self.assertFalse(state.state.messages[0].streaming)
        self.assertFalse(state.state.typing_indicator)


if __name__ == "__main__":
    unittest.main()
