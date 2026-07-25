"""Decision engine for NELA OS."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from brain.context import ContextSnapshot
from brain.intent_router import Intent
from brain.qa import CONVERSATIONAL_ACTIONS


class DecisionType(str, Enum):
    ASK_CLARIFICATION = "ask_clarification"
    EXECUTE_IMMEDIATELY = "execute_immediately"
    WAIT = "wait"
    REMEMBER = "remember"
    DELEGATE = "delegate"
    REJECT = "reject"


@dataclass(frozen=True)
class Decision:
    type: DecisionType
    reason: str
    question: str | None = None
    should_remember: bool = False


class DecisionEngine:
    """Decides whether the Brain can proceed, should ask, or should wait."""

    def decide(self, intent: Intent, context: ContextSnapshot) -> Decision:
        if not intent.raw_text.strip():
            return Decision(
                type=DecisionType.ASK_CLARIFICATION,
                reason="The request is empty.",
                question="אני כאן. מה בא לך שנעשה?",
            )

        if intent.confidence < 0.5:
            return Decision(
                type=DecisionType.ASK_CLARIFICATION,
                reason="Intent confidence is below execution threshold.",
                question="לא לגמרי הבנתי. אפשר לנסח לי את זה כפעולה או שאלה?",
            )

        if context.pending_confirmations:
            return Decision(
                type=DecisionType.WAIT,
                reason="A previous confirmation is still pending.",
            )

        if intent.action in CONVERSATIONAL_ACTIONS:
            return Decision(
                type=DecisionType.EXECUTE_IMMEDIATELY,
                reason="The request can be answered by the conversation QA layer.",
            )

        if intent.action in {"OpenApplication", "CloseApplication", "SwitchApplication"} and not intent.application:
            return Decision(
                type=DecisionType.ASK_CLARIFICATION,
                reason="Missing application slot.",
                question="איזו אפליקציה לפתוח?",
            )

        if intent.action == "PlayMedia" and not intent.application:
            return Decision(
                type=DecisionType.ASK_CLARIFICATION,
                reason="Missing media application slot.",
                question="באיזו אפליקציה לנגן את זה?",
            )

        if intent.requires_confirmation:
            return Decision(
                type=DecisionType.ASK_CLARIFICATION,
                reason="The requested action requires confirmation.",
                question="סגרנו שאמשיך עם הפעולה הזאת?",
            )

        if intent.action == "Remember":
            return Decision(
                type=DecisionType.REMEMBER,
                reason="The user asked NELA to remember information.",
                should_remember=True,
            )

        if intent.action in {"OpenApplication", "SwitchApplication", "PlayMedia"}:
            return Decision(
                type=DecisionType.DELEGATE,
                reason="The request has enough information and a semantic capability.",
            )

        if intent.target_agent:
            return Decision(
                type=DecisionType.DELEGATE,
                reason="The request has enough information and a target capability.",
            )

        return Decision(
            type=DecisionType.ASK_CLARIFICATION,
            reason="No target capability could be inferred.",
            question="מה תרצה שנלה תעשה?",
        )
