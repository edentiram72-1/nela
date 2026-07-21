"""Files agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class FilesAgent(BaseAgent):
    name = "files"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "File operations are not implemented yet.", {"command": command.action})

