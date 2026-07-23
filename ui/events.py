"""Bridge Brain events into UI state."""

from __future__ import annotations

from core.events import Event, EventBus, EventTypes
from ui.state import EyeState, UIStateManager


class UIEventBridge:
    """Subscribes to Brain events and updates UI state without changing Brain."""

    def __init__(self, event_bus: EventBus, state: UIStateManager) -> None:
        self.event_bus = event_bus
        self.state = state

    def start(self) -> None:
        self.event_bus.subscribe("*", self.handle_event)
        self.state.set_brain_status("online")

    def handle_event(self, event: Event) -> None:
        if event.type == EventTypes.INPUT_RECEIVED:
            self.state.set_eye_state(EyeState.LISTENING)
        elif event.type == EventTypes.INTENT_RECOGNIZED:
            self.state.set_eye_state(EyeState.THINKING)
        elif event.type == EventTypes.TASK_STARTED:
            self.state.set_eye_state(EyeState.EXECUTING)
            self.state.add_agent_activity(
                agent=str(event.payload.get("agent", "unknown")),
                action=str(event.payload.get("task_id", "task")),
                status="started",
            )
        elif event.type == EventTypes.TASK_COMPLETED:
            self.state.set_eye_state(EyeState.SUCCESS)
            self.state.add_agent_activity(
                agent=str(event.payload.get("agent", "unknown")),
                action=str(event.payload.get("task_id", "task")),
                status="completed",
            )
        elif event.type in {EventTypes.TASK_FAILED, EventTypes.AGENT_UNAVAILABLE}:
            self.state.set_eye_state(EyeState.ERROR)
            self.state.add_notification("error", str(event.payload.get("message", event.type)))
        elif event.type == EventTypes.MEMORY_UPDATED:
            self.state.add_notification("info", "Memory updated.")
        elif event.type == EventTypes.CONVERSATION_ENDED:
            self.state.set_eye_state(EyeState.IDLE)
            self.state.set_brain_status("idle")
