"""Vision agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class VisionAgent(BaseAgent):
    name = "vision"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Vision delegation is not implemented yet.", {"command": command.action})

