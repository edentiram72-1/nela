"""Reasoning layer for evaluating intents and plans."""

from __future__ import annotations

from dataclasses import dataclass

from brain.intent_router import Intent


@dataclass(frozen=True)
class ReasoningResult:
    accepted: bool
    reason: str


class ReasoningEngine:
    """Applies lightweight policy checks before work is delegated.

    The DecisionEngine owns operational decisions. This class remains a small
    reasoning utility for future plan and safety analysis.
    """

    def evaluate_intent(self, intent: Intent) -> ReasoningResult:
        if not intent.raw_text.strip():
            return ReasoningResult(False, "Empty user request.")
        return ReasoningResult(True, "Intent is actionable.")
