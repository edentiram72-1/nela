"""Voice agent placeholder."""

from __future__ import annotations

from agents.mock import MockAgent


class VoiceAgent(MockAgent):
    name = "voice"
    capability = "voice"
