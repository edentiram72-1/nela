"""Shared safe mock behavior for placeholder Agents."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class MockAgent(BaseAgent):
    """Placeholder Agent that acknowledges delegated work without side effects."""

    capability: str = "generic"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(
            True,
            f"{self.name} mock executed {command.action}.",
            {
                "agent": self.name,
                "capability": self.capability,
                "command": command.action,
                "mock": True,
            },
        )
