"""Authenticated local bridge primitives for future WebView UI hosts."""

from __future__ import annotations

from dataclasses import dataclass, field
import hmac
from pathlib import Path
import secrets
import socket
import tempfile
from uuid import uuid4


@dataclass(frozen=True)
class BridgeRequest:
    """Minimal request metadata the bridge must verify before handling."""

    headers: dict[str, str]
    origin: str | None = None


@dataclass
class SecureLocalBridge:
    """Restricted local transport for UI-to-runtime messages.

    This does not trust the UI as authority; it only authenticates that a local
    UI process launched by this runtime is talking over the expected channel.
    Backend permission checks remain authoritative.
    """

    expected_origin: str = "nela://local-ui"
    socket_dir: Path = field(default_factory=lambda: Path(tempfile.gettempdir()))
    launch_token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    _socket: socket.socket | None = field(default=None, init=False, repr=False)
    socket_path: Path | None = field(default=None, init=False)

    def bind(self) -> Path:
        self.close()
        path = self.socket_dir / f"nela-{uuid4().hex[:12]}.sock"
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(path))
        path.chmod(0o600)
        server.listen(1)
        self._socket = server
        self.socket_path = path
        return path

    def verify_request(self, request: BridgeRequest) -> bool:
        origin = request.origin or request.headers.get("Origin")
        if origin != self.expected_origin:
            return False
        token = request.headers.get("X-NELA-Launch-Token", "")
        return hmac.compare_digest(token, self.launch_token)

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        if self.socket_path and self.socket_path.exists():
            self.socket_path.unlink()
        self.socket_path = None

    @property
    def transport(self) -> str:
        return "unix-domain-socket"
