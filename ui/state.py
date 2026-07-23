"""UI state management for the NELA desktop shell."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Callable
from uuid import uuid4

from ui.theme import ThemeName


class EyeState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    WAITING = "waiting"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SLEEPING = "sleeping"
    OFFLINE = "offline"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ChatMessage:
    role: MessageRole
    content: str
    streaming: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class AgentActivity:
    agent: str
    action: str
    status: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class Notification:
    level: str
    message: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class UIState:
    messages: tuple[ChatMessage, ...] = ()
    agent_activity: tuple[AgentActivity, ...] = ()
    notifications: tuple[Notification, ...] = ()
    eye_state: EyeState = EyeState.IDLE
    brain_status: str = "offline"
    voice_input_active: bool = False
    voice_output_active: bool = False
    typing_indicator: bool = False
    active_theme: ThemeName = ThemeName.DARK


StateListener = Callable[[UIState], None]


class UIStateManager:
    """Central state store synchronized with Brain, Agents, Voice, and Memory."""

    def __init__(self, initial_state: UIState | None = None) -> None:
        self._state = initial_state or UIState()
        self._listeners: list[StateListener] = []

    @property
    def state(self) -> UIState:
        return self._state

    def subscribe(self, listener: StateListener) -> None:
        self._listeners.append(listener)
        listener(self._state)

    def set_brain_status(self, status: str) -> None:
        self._replace(brain_status=status)

    def set_eye_state(self, state: EyeState) -> None:
        self._replace(eye_state=state)

    def set_theme(self, theme: ThemeName | str) -> None:
        self._replace(active_theme=theme if isinstance(theme, ThemeName) else ThemeName(str(theme)))

    def set_voice_input(self, active: bool) -> None:
        self._replace(voice_input_active=active)

    def set_voice_output(self, active: bool) -> None:
        self._replace(voice_output_active=active)

    def set_typing_indicator(self, active: bool) -> None:
        self._replace(typing_indicator=active)

    def add_message(self, role: MessageRole, content: str, streaming: bool = False) -> ChatMessage:
        message = ChatMessage(role=role, content=content, streaming=streaming)
        self._replace(messages=(*self._state.messages, message))
        return message

    def append_to_message(self, message_id: str, content_delta: str, streaming: bool = True) -> None:
        messages = tuple(
            replace(message, content=f"{message.content}{content_delta}", streaming=streaming)
            if message.id == message_id
            else message
            for message in self._state.messages
        )
        self._replace(messages=messages)

    def finish_streaming_message(self, message_id: str) -> None:
        messages = tuple(
            replace(message, streaming=False) if message.id == message_id else message
            for message in self._state.messages
        )
        self._replace(messages=messages)

    def add_agent_activity(self, agent: str, action: str, status: str) -> None:
        activity = AgentActivity(agent=agent, action=action, status=status)
        self._replace(agent_activity=(*self._state.agent_activity, activity))

    def add_notification(self, level: str, message: str) -> None:
        notification = Notification(level=level, message=message)
        self._replace(notifications=(*self._state.notifications, notification))

    def _replace(self, **changes: object) -> None:
        self._state = replace(self._state, **changes)
        for listener in tuple(self._listeners):
            listener(self._state)
