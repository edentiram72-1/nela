"""Automation agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class AutomationAgent(BaseAgent):
    name = "automation"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Automation workflows are not implemented yet.", {"command": command.action})

