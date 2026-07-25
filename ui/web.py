"""Local browser host for the NELA visual prototype."""

from __future__ import annotations

import json
import secrets
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from brain.conversation import ConversationTurn
from brain.decision import DecisionType
from core.startup import NelaRuntime


class NelaWebServer(ThreadingHTTPServer):
    """HTTP server that keeps NELA runtime state alive across browser messages."""

    def __init__(
        self,
        server_address: tuple[str, int],
        runtime: NelaRuntime,
        index_path: Path,
        auth_token: str | None = None,
    ) -> None:
        super().__init__(server_address, NelaWebHandler)
        self.runtime = runtime
        self.index_path = index_path
        self.auth_token = auth_token or secrets.token_urlsafe(32)


class NelaWebHandler(BaseHTTPRequestHandler):
    """Serve the visual prototype and route chat messages into the Brain."""

    server: NelaWebServer

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_html(self._inject_launch_token(self.server.index_path.read_text(encoding="utf-8")))
            return
        if parsed.path == "/health":
            agents = self.server.runtime.dispatcher.discover_agents()
            self._send_json(
                {
                    "ok": True,
                    "agents": list(agents),
                    "agent_count": len(agents),
                }
            )
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/chat":
            self.send_error(404, "Not found")
            return
        if not self._has_valid_bridge_auth():
            self._send_json(
                {
                    "ok": False,
                    "response": "בקשת ה-UI נדחתה כי אימות ההרצה המקומית נכשל.",
                    "eye_state": "error",
                },
                status=403,
            )
            return

        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.loads(body.decode("utf-8") or "{}")
            message = str(payload.get("message", "")).strip()
            if not message:
                raise ValueError("Empty message.")

            turn = self.server.runtime.conversation.handle_text(message)
            response = self.server.runtime.response_adapter.render_and_maybe_speak(turn)
            self._send_json(_turn_payload(turn, response))
        except Exception as error:
            self._send_json(
                {
                    "ok": False,
                    "response": f"נתקעתי רגע: {error}",
                    "eye_state": "error",
                },
                status=500,
            )

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_html(self, html: str) -> None:
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _has_valid_bridge_auth(self) -> bool:
        token = self.headers.get("X-NELA-Launch-Token", "")
        if not secrets.compare_digest(token, self.server.auth_token):
            return False

        origin = self.headers.get("Origin", "")
        return _is_allowed_local_origin(origin, self.server.server_address[1])

    def _inject_launch_token(self, html: str) -> str:
        token_script = (
            "<script>"
            f"window.NELA_BRIDGE_TOKEN = {json.dumps(self.server.auth_token)};"
            "</script>"
        )
        return html.replace("</head>", f"{token_script}\n</head>", 1)


def serve_visual_prototype(runtime: NelaRuntime, index_path: Path, port: int = 0) -> None:
    """Run NELA's browser prototype on a local-only HTTP server."""

    server = NelaWebServer(("127.0.0.1", port), runtime=runtime, index_path=index_path)
    host, selected_port = server.server_address
    url = f"http://{host}:{selected_port}/"
    _open_browser(url)
    print(f"NELA visual prototype running: {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _open_browser(url: str) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "Google Chrome", url], check=False)
        return
    subprocess.run([sys.executable, "-m", "webbrowser", url], check=False)


def _is_allowed_local_origin(origin: str, port: int) -> bool:
    parsed = urlparse(origin)
    if parsed.scheme != "http" or parsed.port != port:
        return False
    return parsed.hostname in {"127.0.0.1", "localhost", "::1"}


def _turn_payload(turn: ConversationTurn, response: str) -> dict[str, Any]:
    return {
        "ok": True,
        "response": response,
        "intent": turn.intent.action,
        "decision": turn.decision.type.value,
        "application": turn.intent.application,
        "resource": turn.intent.resource,
        "plan_tasks": [task.description for task in turn.plan.tasks] if turn.plan else [],
        "agent_results": [
            {"success": result.success, "message": result.message}
            for result in turn.dispatched_results
        ],
        "eye_state": _eye_state_for_turn(turn),
    }


def _eye_state_for_turn(turn: ConversationTurn) -> str:
    if turn.decision.type in {DecisionType.ASK_CLARIFICATION, DecisionType.WAIT}:
        return "waiting"
    if turn.dispatched_results and any(not result.success for result in turn.dispatched_results):
        return "error"
    if turn.plan or turn.dispatched_results:
        return "success"
    return "speaking"
