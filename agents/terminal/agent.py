"""Terminal agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class TerminalAgent(BaseAgent):
    name = "terminal"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Terminal execution is not implemented yet.", {"command": command.action})

