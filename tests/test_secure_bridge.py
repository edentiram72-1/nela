from __future__ import annotations

from pathlib import Path
import socket
import tempfile
import unittest

from ui.secure_bridge import BridgeRequest, SecureLocalBridge


class SecureBridgeTests(unittest.TestCase):
    def test_bridge_binds_unix_domain_socket(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bridge = SecureLocalBridge(socket_dir=Path(directory))
            path = bridge.bind()

            self.assertEqual(bridge.transport, "unix-domain-socket")
            self.assertTrue(path.exists())
            self.assertIsNotNone(bridge._socket)
            self.assertEqual(bridge._socket.family, socket.AF_UNIX)
            bridge.close()
            self.assertFalse(path.exists())

    def test_bridge_rejects_missing_or_wrong_token_and_origin(self) -> None:
        bridge = SecureLocalBridge(launch_token="token")

        self.assertFalse(bridge.verify_request(BridgeRequest(headers={})))
        self.assertFalse(
            bridge.verify_request(
                BridgeRequest(headers={"X-NELA-Launch-Token": "bad"}, origin="nela://local-ui")
            )
        )
        self.assertFalse(
            bridge.verify_request(
                BridgeRequest(headers={"X-NELA-Launch-Token": "token"}, origin="https://evil.local")
            )
        )
        self.assertTrue(
            bridge.verify_request(
                BridgeRequest(headers={"X-NELA-Launch-Token": "token"}, origin="nela://local-ui")
            )
        )


if __name__ == "__main__":
    unittest.main()
