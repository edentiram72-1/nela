"""Voice event helpers."""

from __future__ import annotations

from core.events import Event, EventBus, EventTypes


def publish_voice_event(events: EventBus, event_type: str, payload: dict[str, object] | None = None) -> None:
    events.publish(Event(type=event_type, source="agents.voice", payload=payload or {}))


VOICE_EVENT_TYPES = (
    EventTypes.SPEECH_QUEUED,
    EventTypes.SPEECH_STARTED,
    EventTypes.SPEECH_PAUSED,
    EventTypes.SPEECH_RESUMED,
    EventTypes.SPEECH_COMPLETED,
    EventTypes.SPEECH_INTERRUPTED,
    EventTypes.SPEECH_FAILED,
    EventTypes.VOICE_STATUS_CHANGED,
)
