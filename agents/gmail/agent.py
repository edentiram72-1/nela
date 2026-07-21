"""Gmail agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class GmailAgent(BaseAgent):
    name = "gmail"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Gmail integration is not implemented yet.", {"command": command.action})

