"""GitHub agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class GitHubAgent(BaseAgent):
    name = "github"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "GitHub integration is not implemented yet.", {"command": command.action})

