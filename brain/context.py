"""Conversation and execution context for NELA OS."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class RunningTaskState:
    task_id: str
    description: str
    target_agent: str | None
    started_at: datetime


@dataclass(frozen=True)
class PendingConfirmation:
    id: str
    question: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContextSnapshot:
    conversation_id: str
    current_turn_id: str | None
    last_intent: str | None
    previous_commands: tuple[str, ...]
    open_applications: tuple[str, ...]
    desktop_state: dict[str, Any]
    running_tasks: dict[str, RunningTaskState]
    pending_confirmations: dict[str, PendingConfirmation]
    session_state: dict[str, Any]


class ContextEngine:
    """Tracks current conversation, desktop, task, and confirmation state."""

    def __init__(self) -> None:
        self.conversation_id = str(uuid4())
        self.current_turn_id: str | None = None
        self.last_intent: str | None = None
        self.previous_commands: list[str] = []
        self.open_applications: set[str] = set()
        self.desktop_state: dict[str, Any] = {}
        self.running_tasks: dict[str, RunningTaskState] = {}
        self.pending_confirmations: dict[str, PendingConfirmation] = {}
        self.session_state: dict[str, Any] = {}

    def start_turn(self, user_text: str) -> str:
        self.current_turn_id = str(uuid4())
        self.previous_commands.append(user_text)
        return self.current_turn_id

    def record_intent(self, intent_name: str) -> None:
        self.last_intent = intent_name

    def add_pending_confirmation(self, question: str, metadata: dict[str, Any] | None = None) -> PendingConfirmation:
        confirmation = PendingConfirmation(
            id=str(uuid4()),
            question=question,
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self.pending_confirmations[confirmation.id] = confirmation
        return confirmation

    def oldest_pending_confirmation(self) -> PendingConfirmation | None:
        if not self.pending_confirmations:
            return None
        return min(self.pending_confirmations.values(), key=lambda confirmation: confirmation.created_at)

    def update_confirmation_metadata(self, confirmation_id: str, metadata: dict[str, Any]) -> PendingConfirmation | None:
        confirmation = self.pending_confirmations.get(confirmation_id)
        if confirmation is None:
            return None
        updated = replace(confirmation, metadata=dict(metadata))
        self.pending_confirmations[confirmation_id] = updated
        return updated

    def resolve_confirmation(self, confirmation_id: str) -> None:
        self.pending_confirmations.pop(confirmation_id, None)

    def mark_task_running(self, task_id: str, description: str, target_agent: str | None) -> None:
        self.running_tasks[task_id] = RunningTaskState(
            task_id=task_id,
            description=description,
            target_agent=target_agent,
            started_at=datetime.now(timezone.utc),
        )

    def mark_task_finished(self, task_id: str) -> None:
        self.running_tasks.pop(task_id, None)

    def set_desktop_state(self, state: dict[str, Any]) -> None:
        self.desktop_state = dict(state)

    def add_open_application(self, application: str) -> None:
        self.open_applications.add(application)

    def snapshot(self) -> ContextSnapshot:
        return ContextSnapshot(
            conversation_id=self.conversation_id,
            current_turn_id=self.current_turn_id,
            last_intent=self.last_intent,
            previous_commands=tuple(self.previous_commands),
            open_applications=tuple(sorted(self.open_applications)),
            desktop_state=dict(self.desktop_state),
            running_tasks=dict(self.running_tasks),
            pending_confirmations=dict(self.pending_confirmations),
            session_state=dict(self.session_state),
        )
