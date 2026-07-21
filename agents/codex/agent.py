"""Codex agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class CodexAgent(BaseAgent):
    name = "codex"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Codex automation is not implemented yet.", {"command": command.action})

