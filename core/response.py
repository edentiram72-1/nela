"""Response rendering and voice delegation for Brain turns."""

from __future__ import annotations

from agents.base import AgentResult
from brain.conversation import ConversationTurn
from brain.decision import DecisionType
from brain.dispatcher import AgentDispatcher
from brain.planner import Task
from core.config import AppConfig
from language.engine import LanguageEngine


class NelaResponseAdapter:
    """Converts semantic Brain turns into user-facing Hebrew and optional speech."""

    def __init__(self, language: LanguageEngine, dispatcher: AgentDispatcher, config: AppConfig) -> None:
        self.language = language
        self.dispatcher = dispatcher
        self.config = config

    def render_turn(self, turn: ConversationTurn) -> str:
        category, variables = self._category_and_variables(turn)
        return self.language.render_response(category=category, variables=variables)

    def render_and_maybe_speak(self, turn: ConversationTurn) -> str:
        text = self.render_turn(turn)
        if self.config.voice_auto_speak_responses:
            self.speak_text(text)
        return text

    def speak_text(self, text: str) -> AgentResult | None:
        if "voice" not in self.dispatcher.discover_agents():
            return None
        task = Task(
            description="Speak final assistant response",
            action="speak",
            target_agent="voice",
            payload={
                "text": text,
                "interrupt": True,
                "silent": self.config.voice_silent_mode,
            },
            timeout_seconds=10.0,
        )
        return self.dispatcher.dispatch(task, plan_id="response-output")

    def _category_and_variables(self, turn: ConversationTurn) -> tuple[str, dict[str, object]]:
        application = turn.intent.application or "האפליקציה"
        resource = turn.intent.resource or "הבקשה"

        variables: dict[str, object] = {
            "application": application,
            "resource": resource,
            "message": turn.message,
            "intent": turn.intent.action,
        }

        if turn.decision.type in {DecisionType.ASK_CLARIFICATION, DecisionType.WAIT}:
            variables["question"] = turn.message
            return "clarifications.ask", variables
        if turn.decision.type == DecisionType.REJECT:
            return "confirmations.cancelled", variables
        if turn.dispatched_results and any(not result.success for result in turn.dispatched_results):
            failed = next(result for result in turn.dispatched_results if not result.success)
            variables["error"] = failed.message
            return "errors.general", variables
        if turn.intent.action == "OpenApplication":
            return "desktop.open.success", variables
        if turn.intent.action == "CloseApplication":
            return "desktop.close.success", variables
        if turn.intent.action == "PlayMedia":
            return "music.play.success", variables
        if turn.intent.action == "Remember":
            return "memory.remember.success", variables
        if turn.plan:
            return "success.general", variables
        return "general_chat.response", variables
