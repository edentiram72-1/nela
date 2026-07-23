"""Desktop agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class DesktopAgent(BaseAgent):
    name = "desktop"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Desktop control is not implemented yet.", {"command": command.action})

