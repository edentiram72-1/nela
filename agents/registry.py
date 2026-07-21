"""Agent registry for discovery and delegation."""

from __future__ import annotations

from agents.base import BaseAgent


class AgentRegistry:
    """Stores available agents by name."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def unregister(self, name: str) -> bool:
        return self._agents.pop(name, None) is not None

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._agents))

    def health_check(self) -> dict[str, object]:
        return {name: agent.health_check() for name, agent in self._agents.items()}
