"""Event primitives and in-process event bus."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import time
from typing import Any, Callable, DefaultDict
from uuid import uuid4

EventHandler = Callable[["Event"], None]


class EventTypes:
    """Shared event names used across modules."""

    INPUT_RECEIVED = "InputReceived"
    INTENT_RECOGNIZED = "IntentRecognized"
    DECISION_MADE = "DecisionMade"
    PLAN_CREATED = "PlanCreated"
    TASK_CREATED = "TaskCreated"
    TASK_DISPATCHED = "TaskDispatched"
    TASK_STARTED = "TaskStarted"
    TASK_COMPLETED = "TaskCompleted"
    TASK_FAILED = "TaskFailed"
    TASK_CANCELLED = "TaskCancelled"
    AGENT_STATUS_CHANGED = "AgentStatusChanged"
    AGENT_UNAVAILABLE = "AgentUnavailable"
    MEMORY_UPDATED = "MemoryUpdated"
    MEMORY_RETRIEVED = "MemoryRetrieved"
    CONTEXT_UPDATED = "ContextUpdated"
    CONFIRMATION_REQUESTED = "ConfirmationRequested"
    CONFIRMATION_RESOLVED = "ConfirmationResolved"
    CONFIRMATION_EXPIRED = "ConfirmationExpired"
    PERMISSION_REQUESTED = "PermissionRequested"
    PERMISSION_GRANTED = "PermissionGranted"
    PERMISSION_DENIED = "PermissionDenied"
    SCOPE_VIOLATION = "ScopeViolation"
    ACTION_EXECUTED = "ActionExecuted"
    ACTION_ROLLED_BACK = "ActionRolledBack"
    KILL_SWITCH_ACTIVATED = "KillSwitchActivated"
    KILL_SWITCH_DEACTIVATED = "KillSwitchDeactivated"
    LOCK_MODE_CHANGED = "LockModeChanged"
    EVENT_SUBSCRIBER_FAILED = "EventSubscriberFailed"
    EVENT_SUBSCRIBER_SLOW = "EventSubscriberSlow"
    EVENT_LOOP_DETECTED = "EventLoopDetected"
    SPEECH_QUEUED = "SpeechQueued"
    SPEECH_STARTED = "SpeechStarted"
    SPEECH_PAUSED = "SpeechPaused"
    SPEECH_RESUMED = "SpeechResumed"
    SPEECH_COMPLETED = "SpeechCompleted"
    SPEECH_INTERRUPTED = "SpeechInterrupted"
    SPEECH_FAILED = "SpeechFailed"
    VOICE_STATUS_CHANGED = "VoiceStatusChanged"
    CONVERSATION_ENDED = "ConversationEnded"


@dataclass(frozen=True)
class Event:
    """A single immutable system event."""

    type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    """Simple synchronous event bus for local module communication."""

    def __init__(
        self,
        max_history: int = 1000,
        slow_handler_seconds: float = 0.25,
        max_publish_depth: int = 32,
    ) -> None:
        self._subscribers: DefaultDict[str, list[EventHandler]] = defaultdict(list)
        self._history: deque[Event] = deque(maxlen=max_history)
        self._logger = logging.getLogger("nela.brain")
        self._slow_handler_seconds = slow_handler_seconds
        self._max_publish_depth = max_publish_depth
        self._publish_depth = 0

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        if self._publish_depth >= self._max_publish_depth:
            self._append_internal_event(
                EventTypes.EVENT_LOOP_DETECTED,
                {
                    "blocked_event": event.type,
                    "blocked_event_id": event.id,
                    "correlation_id": event.correlation_id,
                    "max_publish_depth": self._max_publish_depth,
                },
                event.correlation_id,
            )
            return

        self._history.append(event)
        self._logger.info("event=%s source=%s id=%s", event.type, event.source, event.id)
        self._publish_depth += 1
        try:
            for handler in self._handlers_for(event.type):
                self._call_handler(handler, event)
        finally:
            self._publish_depth -= 1

    def history(self) -> tuple[Event, ...]:
        return tuple(self._history)

    def clear_history(self) -> None:
        self._history.clear()

    def _handlers_for(self, event_type: str) -> tuple[EventHandler, ...]:
        return tuple(self._subscribers.get(event_type, ())) + tuple(self._subscribers.get("*", ()))

    def _call_handler(self, handler: EventHandler, event: Event) -> None:
        started_at = time.monotonic()
        try:
            handler(event)
        except Exception as error:
            self._logger.exception("event_subscriber_failed event=%s handler=%r", event.type, handler)
            self._append_internal_event(
                EventTypes.EVENT_SUBSCRIBER_FAILED,
                {
                    "event_type": event.type,
                    "event_id": event.id,
                    "handler": _handler_name(handler),
                    "error_type": error.__class__.__name__,
                    "error": str(error),
                },
                event.correlation_id,
            )
            return

        elapsed = time.monotonic() - started_at
        if elapsed > self._slow_handler_seconds:
            self._append_internal_event(
                EventTypes.EVENT_SUBSCRIBER_SLOW,
                {
                    "event_type": event.type,
                    "event_id": event.id,
                    "handler": _handler_name(handler),
                    "elapsed_seconds": elapsed,
                    "threshold_seconds": self._slow_handler_seconds,
                },
                event.correlation_id,
            )

    def _append_internal_event(self, event_type: str, payload: dict[str, Any], correlation_id: str | None) -> None:
        self._history.append(
            Event(
                type=event_type,
                source="core.events",
                payload=payload,
                correlation_id=correlation_id,
            )
        )


def _handler_name(handler: EventHandler) -> str:
    return getattr(handler, "__qualname__", getattr(handler, "__name__", repr(handler)))
