"""Spotify agent placeholder."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, BaseAgent


class SpotifyAgent(BaseAgent):
    name = "spotify"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(False, "Spotify control is not implemented yet.", {"command": command.action})

