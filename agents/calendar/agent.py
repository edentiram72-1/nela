"""Calendar agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class CalendarAgent(BaseAgent):
    name = "calendar"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Calendar integration is not implemented yet.", {"command": command.action})

