"""Browser agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class BrowserAgent(BaseAgent):
    name = "browser"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Browser control is not implemented yet.", {"command": command.action})

