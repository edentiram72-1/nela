"""Routes UI actions into the NELA Brain."""

from __future__ import annotations

from brain.conversation import ConversationTurn
from core.startup import NelaRuntime
from ui.state import EyeState, MessageRole, UIStateManager


class UIRouter:
    """Connects user input from the UI to the existing Brain runtime."""

    def __init__(self, runtime: NelaRuntime, state: UIStateManager) -> None:
        self.runtime = runtime
        self.state = state

    def submit_text(self, text: str) -> ConversationTurn:
        normalized = text.strip()
        if not normalized:
            raise ValueError("Cannot submit an empty message.")

        self.state.add_message(MessageRole.USER, normalized)
        self.state.set_typing_indicator(True)
        self.state.set_eye_state(EyeState.THINKING)

        try:
            turn = self.runtime.conversation.handle_text(normalized)
        except Exception:
            self.state.set_typing_indicator(False)
            self.state.set_eye_state(EyeState.ERROR)
            raise

        response_text = self.runtime.response_adapter.render_and_maybe_speak(turn)
        self.state.set_typing_indicator(False)
        self.state.add_message(MessageRole.ASSISTANT, response_text)
        return turn

    def start_streaming_response(self) -> str:
        message = self.state.add_message(MessageRole.ASSISTANT, "", streaming=True)
        self.state.set_typing_indicator(True)
        return message.id

    def append_streaming_response(self, message_id: str, content_delta: str) -> None:
        self.state.append_to_message(message_id, content_delta, streaming=True)

    def finish_streaming_response(self, message_id: str) -> None:
        self.state.finish_streaming_message(message_id)
        self.state.set_typing_indicator(False)


def format_turn_markdown(turn: ConversationTurn) -> str:
    """Format a Brain turn as Markdown for the chat component."""

    lines = [
        "### NELA Brain",
        f"- **Intent:** `{turn.intent.action}`",
        f"- **Decision:** `{turn.decision.type.value}`",
        f"- **Message:** {turn.message}",
    ]
    if turn.intent.application:
        lines.append(f"- **Application:** {turn.intent.application}")
    if turn.intent.resource:
        lines.append(f"- **Resource:** {turn.intent.resource}")
    if turn.plan:
        lines.append("")
        lines.append("```text")
        for index, task in enumerate(turn.plan.tasks, start=1):
            target = task.target_agent or "unassigned"
            lines.append(f"{index}. {task.description} -> {target}.{task.action}")
        lines.append("```")
    if turn.dispatched_results:
        lines.append("")
        lines.append("**Agent results:**")
        for result in turn.dispatched_results:
            status = "ok" if result.success else "failed"
            lines.append(f"- `{status}` {result.message}")
    return "\n".join(lines)
