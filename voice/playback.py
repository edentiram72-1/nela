"""Playback state for spoken output."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlaybackState:
    enabled: bool = True
    paused: bool = False
    current_utterance_id: str | None = None
