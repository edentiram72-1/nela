"""Local browser-hosted vertical-slice demo for NELA OS."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import socket
from threading import Lock
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
import webbrowser

from core.config import AppConfig
from core.startup import NelaRuntime, bootstrap
from ui.events import UIEventBridge
from ui.router import UIRouter
from ui.state import EyeState, MessageRole, UIState, UIStateManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EYE_HTML = PROJECT_ROOT / "design" / "nela_living_eye.html"


class NelaDemoController:
    """Runs the existing Brain, UI state bridge, Language Engine, and Voice Agent."""

    def __init__(self, runtime: NelaRuntime) -> None:
        self.runtime = runtime
        self.state = UIStateManager()
        self.router = UIRouter(runtime=runtime, state=self.state)
        self._lock = Lock()
        self._eye_states: list[str] = [EyeState.IDLE.value]
        self.bridge = UIEventBridge(runtime.events, self.state)
        self.state.subscribe(self._record_eye_state)
        self.bridge.start()

    @classmethod
    def from_config(cls, config: AppConfig | None = None) -> "NelaDemoController":
        base_config = config or AppConfig.from_env()
        demo_config = replace(base_config, enable_voice=True, voice_auto_speak_responses=True)
        return cls(bootstrap(demo_config))

    def process_message(self, text: str) -> dict[str, Any]:
        normalized = text.strip()
        if not normalized:
            raise ValueError("Message is empty.")

        with self._lock:
            state_start = len(self._eye_states)
            events_start = len(self.runtime.events.history())
            turn = self.router.submit_text(normalized)
            response = self._latest_assistant_message(self.state.state)
            if self.state.state.eye_state not in {EyeState.IDLE, EyeState.WAITING, EyeState.ERROR}:
                self.state.set_eye_state(EyeState.IDLE)

            eye_states = self._collapse_states(self._eye_states[state_start:])
            if not eye_states or eye_states[-1] != self.state.state.eye_state.value:
                eye_states.append(self.state.state.eye_state.value)

            return {
                "response": response,
                "intent": turn.intent.action,
                "decision": turn.decision.type.value,
                "application": turn.intent.application,
                "eye_states": eye_states,
                "events": [event.type for event in self.runtime.events.history()[events_start:]],
                "plan": [
                    {
                        "description": task.description,
                        "target_agent": task.target_agent,
                        "action": task.action,
                    }
                    for task in (turn.plan.tasks if turn.plan else ())
                ],
                "agent_results": [
                    {
                        "success": result.success,
                        "message": result.message,
                        "data": result.data,
                    }
                    for result in turn.dispatched_results
                ],
                "final_eye_state": self.state.state.eye_state.value,
                "voice_output_active": self.state.state.voice_output_active,
            }

    def snapshot(self) -> dict[str, Any]:
        state = self.state.state
        return {
            "eye_state": state.eye_state.value,
            "brain_status": state.brain_status,
            "voice_output_active": state.voice_output_active,
            "messages": [
                {"role": message.role.value, "content": message.content}
                for message in state.messages
            ],
        }

    def _record_eye_state(self, state: UIState) -> None:
        value = state.eye_state.value
        if not self._eye_states or self._eye_states[-1] != value:
            self._eye_states.append(value)

    @staticmethod
    def _collapse_states(states: list[str]) -> list[str]:
        collapsed: list[str] = []
        for state in states:
            if not collapsed or collapsed[-1] != state:
                collapsed.append(state)
        return collapsed

    @staticmethod
    def _latest_assistant_message(state: UIState) -> str:
        for message in reversed(state.messages):
            if message.role == MessageRole.ASSISTANT:
                return message.content
        return ""


class NelaDemoServer(ThreadingHTTPServer):
    """HTTP server carrying the demo controller."""

    def __init__(self, server_address: tuple[str, int], controller: NelaDemoController) -> None:
        super().__init__(server_address, NelaDemoHandler)
        self.controller = controller


class NelaDemoHandler(BaseHTTPRequestHandler):
    """Serves the local UI and routes chat messages to the Brain."""

    server: NelaDemoServer

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self._send_html(render_index_html())
            return
        if self.path == "/eye":
            self._send_html(render_eye_html())
            return
        if self.path == "/api/state":
            self._send_json(self.server.controller.snapshot())
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/api/message":
            self.send_error(404)
            return
        try:
            payload = json.loads(self.rfile.read(_content_length(self.headers)).decode("utf-8"))
            result = self.server.controller.process_message(str(payload.get("text", "")))
        except Exception as error:
            self._send_json({"error": str(error), "eye_states": [EyeState.ERROR.value, EyeState.IDLE.value]}, status=400)
            return
        self._send_json(result)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
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


def render_index_html() -> str:
    return """<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NELA OS</title>
<style>
:root{color-scheme:dark;--bg:#080514;--panel:#120b26;--line:rgba(160,140,255,.18);--text:#ede8ff;--muted:#a59dc9;--accent:#37b8a8;--danger:#ff4d5e}
*{box-sizing:border-box}html,body{height:100%}body{margin:0;background:var(--bg);color:var(--text);font-family:Assistant,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;overflow:hidden}
.app{height:100%;display:grid;grid-template-columns:minmax(360px,44vw) 1fr}
.eye-pane{position:relative;min-width:0;border-left:1px solid var(--line);background:#070411}
.eye-frame{width:100%;height:100%;border:0;display:block}
.work{display:grid;grid-template-rows:auto 1fr auto;min-width:0;background:linear-gradient(180deg,#120b26 0%,#080514 100%)}
header{padding:22px 28px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{font-weight:800;letter-spacing:.22em;font-size:13px;color:var(--muted);direction:ltr}.state{font-size:13px;color:var(--accent);font-family:"Space Grotesk",monospace;text-transform:uppercase;direction:ltr}
.thread{padding:24px 28px;overflow:auto;display:flex;flex-direction:column;gap:12px}
.msg{max-width:min(74%,720px);padding:12px 16px;border:1px solid var(--line);line-height:1.48;font-size:16px;white-space:pre-wrap}
.msg.user{align-self:flex-start;background:#241a4a;border-radius:16px 16px 4px 16px}.msg.nela{align-self:flex-end;background:rgba(255,255,255,.045);border-right:2px solid var(--accent);border-radius:16px 16px 16px 4px}.msg.error{border-color:var(--danger);color:#ffd8dd}
.composer{display:flex;gap:10px;padding:18px 28px 24px;border-top:1px solid var(--line)}
input{flex:1;min-width:0;border:1px solid var(--line);background:#0b0718;color:var(--text);font:400 17px inherit;padding:14px 16px;outline:none}
input:focus{border-color:var(--accent);box-shadow:0 0 0 1px rgba(55,184,168,.35)}
button{border:0;background:var(--accent);color:#03100e;font-weight:800;font-size:15px;padding:0 22px;cursor:pointer}
button:disabled{opacity:.45;cursor:not-allowed}.meta{font-size:12px;color:var(--muted);direction:ltr;margin-top:4px}
@media (max-width:760px){.app{grid-template-columns:1fr;grid-template-rows:42vh 1fr}.eye-pane{border-left:0;border-bottom:1px solid var(--line)}header,.thread,.composer{padding-left:18px;padding-right:18px}.msg{max-width:92%}}
</style>
</head>
<body>
<main class="app">
  <section class="eye-pane" aria-label="NELA Living Eye">
    <iframe id="eye" class="eye-frame" src="/eye" title="NELA Living Eye"></iframe>
  </section>
  <section class="work" aria-label="NELA Chat">
    <header><div class="brand">NELA OS</div><div class="state" id="state">idle</div></header>
    <div class="thread" id="thread">
      <div class="msg nela">אני איתך. אפשר לכתוב לי בעברית.</div>
    </div>
    <form class="composer" id="composer">
      <input id="input" autocomplete="off" placeholder="נלה, תפתחי את Spotify" aria-label="כתוב לנלה">
      <button id="send" type="submit">שלחי</button>
    </form>
  </section>
</main>
<script>
const eye = document.getElementById('eye');
const thread = document.getElementById('thread');
const input = document.getElementById('input');
const send = document.getElementById('send');
const stateLabel = document.getElementById('state');
function setEyeState(state){
  stateLabel.textContent = state;
  try{
    eye.contentWindow.postMessage({type:'nela:set-state', state}, '*');
    const doc = eye.contentDocument;
    if(doc){ doc.body.dataset.state = state; const word = doc.getElementById('stateWord'); if(word) word.textContent = state; }
  }catch(error){}
}
function addMessage(role, text, kind=''){
  const node = document.createElement('div');
  node.className = `msg ${role} ${kind}`.trim();
  node.textContent = text;
  thread.appendChild(node);
  thread.scrollTop = thread.scrollHeight;
}
async function playStates(states){
  const visible = states && states.length ? states : ['idle'];
  for(const state of visible){
    setEyeState(state);
    await new Promise(resolve => setTimeout(resolve, state === 'speaking' ? 900 : 430));
  }
  if(visible[visible.length - 1] !== 'idle') setEyeState('idle');
}
document.getElementById('composer').addEventListener('submit', async event => {
  event.preventDefault();
  const text = input.value.trim();
  if(!text) return;
  input.value = '';
  input.disabled = true; send.disabled = true;
  addMessage('user', text);
  setEyeState('thinking');
  try{
    const response = await fetch('/api/message', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({text})
    });
    const data = await response.json();
    await playStates(data.eye_states || []);
    if(!response.ok) throw new Error(data.error || 'NELA failed.');
    addMessage('nela', data.response || '');
    if(data.intent){
      const meta = document.createElement('div');
      meta.className = 'meta';
      meta.textContent = `${data.intent}${data.application ? ' / ' + data.application : ''}`;
      thread.lastElementChild.appendChild(meta);
    }
  }catch(error){
    setEyeState('error');
    addMessage('nela', String(error.message || error), 'error');
    setTimeout(()=>setEyeState('idle'), 900);
  }finally{
    input.disabled = false; send.disabled = false; input.focus();
  }
});
eye.addEventListener('load', () => setEyeState('idle'));
input.focus();
</script>
</body>
</html>"""


def render_eye_html() -> str:
    source = EYE_HTML.read_text(encoding="utf-8")
    style = """
.chat,.console{display:none!important}
body{grid-template-rows:1fr!important;min-height:100vh!important}
.stage{height:100vh!important;padding:24px!important}
.eye-wrap{width:min(68vh,82vw,560px)!important}
"""
    script = """
<script>
window.addEventListener('message', function(event){
  if(!event.data || event.data.type !== 'nela:set-state') return;
  var state = String(event.data.state || 'idle');
  document.body.dataset.state = state;
  var word = document.getElementById('stateWord');
  if(word) word.textContent = state;
});
</script>
"""
    source = source.replace("</style>", f"{style}\n</style>", 1)
    return source.replace("</body>", f"{script}\n</body>", 1)


def _content_length(headers: Any) -> int:
    try:
        return int(headers.get("Content-Length", "0"))
    except ValueError:
        return 0


def _find_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        result = probe.connect_ex(("127.0.0.1", preferred))
        if result != 0:
            return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the visible NELA desktop demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically.")
    parser.add_argument("--headless-smoke", action="store_true", help="Bootstrap the demo without opening a browser.")
    args = parser.parse_args()

    controller = NelaDemoController.from_config()
    if args.headless_smoke:
        print("NELA vertical slice runtime bootstrapped.")
        return

    port = _find_port(args.port)
    server = NelaDemoServer((args.host, port), controller)
    url = f"http://{args.host}:{port}/"
    print(f"NELA vertical slice is running at {url}")
    print("Press Ctrl+C to stop.")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
