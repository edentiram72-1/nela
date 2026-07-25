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
            "task_hint": turn.message,
        }
        response_variables = turn.intent.parameters.get("response_variables")
        if isinstance(response_variables, dict):
            variables.update(response_variables)

        response_category = turn.intent.parameters.get("response_category")
        if isinstance(response_category, str) and response_category:
            return response_category, variables

        if turn.decision.type in {DecisionType.ASK_CLARIFICATION, DecisionType.WAIT}:
            variables["question"] = turn.message
            variables["clarify"] = turn.message
            return "clarify.one_question", variables
        if turn.decision.type == DecisionType.REJECT:
            return "success.short", variables
        if turn.dispatched_results and any(not result.success for result in turn.dispatched_results):
            failed = next(result for result in turn.dispatched_results if not result.success)
            variables["error"] = failed.message
            variables["what"] = failed.message
            return "error.recovering", variables
        if turn.intent.action == "OpenApplication":
            return "desktop.launch", variables
        if turn.intent.action == "CloseApplication":
            return "desktop.closed", variables
        if turn.intent.action == "PlayMedia":
            return "media.play", variables
        if turn.intent.action == "Remember":
            return "learning.saved", variables
        if turn.plan:
            return "success.short", variables
        return "smalltalk.daily", variables
