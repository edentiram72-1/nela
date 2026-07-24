"""Bridge Brain events into UI state."""

from __future__ import annotations

from collections.abc import Callable

from core.events import Event, EventBus, EventTypes
from ui.state import EyeState, UIStateManager

EVENT_TO_EYE_STATE: dict[str, EyeState] = {
    EventTypes.INPUT_RECEIVED: EyeState.LISTENING,
    EventTypes.INTENT_RECOGNIZED: EyeState.THINKING,
    EventTypes.DECISION_MADE: EyeState.THINKING,
    EventTypes.TASK_DISPATCHED: EyeState.EXECUTING,
    EventTypes.TASK_STARTED: EyeState.EXECUTING,
    EventTypes.CONFIRMATION_REQUESTED: EyeState.WAITING,
    EventTypes.PERMISSION_REQUESTED: EyeState.WAITING,
    EventTypes.TASK_COMPLETED: EyeState.SUCCESS,
    EventTypes.TASK_FAILED: EyeState.ERROR,
    EventTypes.AGENT_UNAVAILABLE: EyeState.ERROR,
    EventTypes.PERMISSION_DENIED: EyeState.ERROR,
    EventTypes.SCOPE_VIOLATION: EyeState.ERROR,
    EventTypes.KILL_SWITCH_ACTIVATED: EyeState.ERROR,
    EventTypes.SPEECH_STARTED: EyeState.SPEAKING,
    EventTypes.SPEECH_COMPLETED: EyeState.IDLE,
    EventTypes.SPEECH_FAILED: EyeState.ERROR,
    EventTypes.CONVERSATION_ENDED: EyeState.IDLE,
}

MOMENT_STATES = {EyeState.SUCCESS, EyeState.WARNING, EyeState.ERROR}


class UIEventBridge:
    """Subscribes to Brain events and updates UI state without changing Brain."""

    def __init__(
        self,
        event_bus: EventBus,
        state: UIStateManager,
        schedule_idle: Callable[[int, Callable[[], None]], object] | None = None,
        moment_duration_ms: int = 3000,
    ) -> None:
        self.event_bus = event_bus
        self.state = state
        self.schedule_idle = schedule_idle
        self.moment_duration_ms = moment_duration_ms

    def start(self) -> None:
        self.event_bus.subscribe("*", self.handle_event)
        self.state.set_brain_status("online")

    def handle_event(self, event: Event) -> None:
        eye_state = None if _is_voice_task_completion(event) else EVENT_TO_EYE_STATE.get(event.type)
        if eye_state is not None:
            self._set_eye_state(eye_state)

        if event.type in {EventTypes.TASK_DISPATCHED, EventTypes.TASK_STARTED}:
            self.state.add_agent_activity(
                agent=str(event.payload.get("agent", "unknown")),
                action=str(event.payload.get("task_id", "task")),
                status="started",
            )
        elif event.type == EventTypes.TASK_COMPLETED:
            self.state.add_agent_activity(
                agent=str(event.payload.get("agent", "unknown")),
                action=str(event.payload.get("task_id", "task")),
                status="completed",
            )
        elif event.type in {EventTypes.TASK_FAILED, EventTypes.AGENT_UNAVAILABLE}:
            self.state.add_notification("error", str(event.payload.get("message", event.type)))
        elif event.type == EventTypes.MEMORY_UPDATED:
            self.state.add_notification("info", "Memory updated.")
        elif event.type == EventTypes.SPEECH_STARTED:
            self.state.set_voice_output(True)
        elif event.type == EventTypes.SPEECH_COMPLETED:
            self.state.set_voice_output(False)
        elif event.type == EventTypes.SPEECH_FAILED:
            self.state.set_voice_output(False)
            self.state.add_notification("error", str(event.payload.get("error", event.type)))
        elif event.type == EventTypes.CONVERSATION_ENDED:
            self.state.set_brain_status("idle")

    def _set_eye_state(self, eye_state: EyeState) -> None:
        self.state.set_eye_state(eye_state)
        if self.schedule_idle and eye_state in MOMENT_STATES:
            self.schedule_idle(self.moment_duration_ms, lambda: self.state.set_eye_state(EyeState.IDLE))


def _is_voice_task_completion(event: Event) -> bool:
    return event.type == EventTypes.TASK_COMPLETED and event.payload.get("agent") == "voice"
