import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from core.config import AppConfig
from core.startup import bootstrap
from ui.web import NelaWebServer


class UIWebTests(unittest.TestCase):
    def test_chat_endpoint_routes_message_through_brain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = bootstrap(
                AppConfig(
                    environment="test",
                    data_dir=root / "data",
                    plugin_dir=root / "plugins",
                    enable_voice=False,
                    voice_auto_speak_responses=False,
                )
            )
            server = NelaWebServer(
                ("127.0.0.1", 0),
                runtime=runtime,
                index_path=Path("design/nela_living_eye.html"),
                auth_token="test-token",
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/api/chat"
                request = urllib.request.Request(
                    url,
                    data=json.dumps({"message": "נלה, תפתחי את Spotify"}).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Origin": f"http://127.0.0.1:{server.server_address[1]}",
                        "X-NELA-Launch-Token": "test-token",
                    },
                    method="POST",
                )

                with urllib.request.urlopen(request, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["intent"], "OpenApplication")
        self.assertEqual(payload["application"], "Spotify")
        self.assertRegex(payload["response"], r"[\u0590-\u05ff]")

    def test_chat_endpoint_rejects_missing_launch_token(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = bootstrap(
                AppConfig(
                    environment="test",
                    data_dir=root / "data",
                    plugin_dir=root / "plugins",
                    enable_voice=False,
                    voice_auto_speak_responses=False,
                )
            )
            server = NelaWebServer(
                ("127.0.0.1", 0),
                runtime=runtime,
                index_path=Path("design/nela_living_eye.html"),
                auth_token="test-token",
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/api/chat"
                request = urllib.request.Request(
                    url,
                    data=json.dumps({"message": "מי את?"}).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Origin": f"http://127.0.0.1:{server.server_address[1]}",
                    },
                    method="POST",
                )

                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(request, timeout=5)
            finally:
                server.shutdown()
                server.server_close()

        self.assertEqual(error.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
