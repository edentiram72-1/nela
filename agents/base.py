"""Shared agent contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class AgentState(str, Enum):
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass(frozen=True)
class AgentCommand:
    action: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class AgentResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class every agent must implement."""

    name: str

    def __init__(self) -> None:
        self._state = AgentState.CREATED

    def initialize(self) -> AgentResult:
        self._state = AgentState.READY
        return AgentResult(True, f"{self.name} initialized.")

    @abstractmethod
    def execute(self, command: AgentCommand) -> AgentResult:
        """Execute one command."""

    def stop(self) -> AgentResult:
        self._state = AgentState.STOPPED
        return AgentResult(True, f"{self.name} stopped.")

    def status(self) -> AgentState:
        return self._state

    def health_check(self) -> AgentResult:
        return AgentResult(
            success=self._state != AgentState.ERROR,
            message=f"{self.name} health is {self._state.value}.",
            data={"state": self._state.value},
        )

