"""Agent registry for discovery and delegation."""

from __future__ import annotations

from agents.base import BaseAgent


class DuplicateAgentError(ValueError):
    """Raised when an Agent ID is already registered."""


class AgentNotRegisteredError(ValueError):
    """Raised when replacing an Agent that is not already registered."""


class AgentRegistry:
    """Stores available agents by name."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self.registration_audit: list[dict[str, str]] = []

    def register(self, agent: BaseAgent) -> None:
        self._store(agent, result="registered", expect_exists=False)

    def replace(self, agent: BaseAgent) -> None:
        self._store(agent, result="replaced", expect_exists=True)

    def _store(self, agent: BaseAgent, result: str, *, expect_exists: bool) -> None:
        exists = agent.name in self._agents
        if expect_exists and not exists:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_missing"})
            raise AgentNotRegisteredError(f"Agent '{agent.name}' is not registered.")
        if not expect_exists and exists:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_duplicate"})
            raise DuplicateAgentError(f"Agent '{agent.name}' is already registered.")
        self._agents.update({agent.name: agent})
        self.registration_audit.append({"agent": agent.name, "result": result})

    def unregister(self, name: str) -> bool:
        return self._agents.pop(name, None) is not None

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._agents))

    def manifests(self) -> dict[str, object]:
        """Return optional Agent manifests for capability discovery."""

        manifests: dict[str, object] = {}
        for name, agent in self._agents.items():
            manifest = getattr(agent, "manifest", None)
            if manifest is None:
                continue
            to_dict = getattr(manifest, "to_dict", None)
            manifests[name] = to_dict() if callable(to_dict) else manifest
        return manifests

    def health_check(self) -> dict[str, object]:
        return {name: agent.health_check() for name, agent in self._agents.items()}
