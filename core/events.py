"""Event primitives and in-process event bus."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
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

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, list[EventHandler]] = defaultdict(list)
        self._history: list[Event] = []
        self._logger = logging.getLogger("nela.brain")

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        self._history.append(event)
        self._logger.info("event=%s source=%s id=%s", event.type, event.source, event.id)
        for handler in self._subscribers.get(event.type, []):
            handler(event)
        for handler in self._subscribers.get("*", []):
            handler(event)

    def history(self) -> tuple[Event, ...]:
        return tuple(self._history)

    def clear_history(self) -> None:
        self._history.clear()
