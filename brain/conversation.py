"""Conversation orchestration for NELA OS."""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Literal

from agents.base import AgentResult
from brain.context import ContextEngine, PendingConfirmation
from brain.decision import Decision, DecisionEngine, DecisionType
from brain.dispatcher import AgentDispatcher
from brain.applications import resolve_application_alias
from brain.intent_router import Intent, IntentRouter
from brain.memory_manager import MemoryManager
from brain.planner import Plan, Planner, Task, TaskMode, _action_to_command
from brain.qa import CONVERSATIONAL_ACTIONS, KnowledgeEngine
from core.events import Event, EventBus, EventTypes
from permissions.confirmation import action_tuple_hash


@dataclass(frozen=True)
class ConversationTurn:
    """Result of one user interaction with the Brain."""

    user_text: str
    input_mode: str
    intent: Intent
    decision: Decision
    plan: Plan | None
    message: str
    dispatched_results: tuple[AgentResult, ...] = ()


class ConversationEngine:
    """Central Brain entry point for text and voice conversation."""

    def __init__(
        self,
        intent_router: IntentRouter,
        decision_engine: DecisionEngine,
        planner: Planner,
        memory: MemoryManager,
        context: ContextEngine,
        dispatcher: AgentDispatcher,
        events: EventBus,
        auto_dispatch: bool = True,
        confirmation_ttl_seconds: int = 300,
        max_unclear_confirmation_replies: int = 2,
        knowledge: KnowledgeEngine | None = None,
    ) -> None:
        self.intent_router = intent_router
        self.decision_engine = decision_engine
        self.planner = planner
        self.memory = memory
        self.context = context
        self.dispatcher = dispatcher
        self.events = events
        self.auto_dispatch = auto_dispatch
        self.confirmation_ttl = timedelta(seconds=confirmation_ttl_seconds)
        self.max_unclear_confirmation_replies = max_unclear_confirmation_replies
        self.knowledge = knowledge or KnowledgeEngine()
        self.logger = logging.getLogger("nela.brain")

    def handle_text(self, text: str) -> ConversationTurn:
        return self._handle_input(text=text, input_mode="text")

    def handle_voice(self, transcript: str) -> ConversationTurn:
        return self._handle_input(text=transcript, input_mode="voice")

    def end_conversation(self) -> None:
        self.events.publish(
            Event(
                type=EventTypes.CONVERSATION_ENDED,
                source="brain.conversation",
                payload={"conversation_id": self.context.conversation_id},
            )
        )

    def _handle_input(self, text: str, input_mode: str) -> ConversationTurn:
        turn_id = self.context.start_turn(text)
        self.events.publish(
            Event(
                type=EventTypes.INPUT_RECEIVED,
                source="brain.conversation",
                payload={"turn_id": turn_id, "input_mode": input_mode},
            )
        )

        self._expire_pending_confirmations(turn_id)
        pending_confirmation = self.context.oldest_pending_confirmation()
        if pending_confirmation is not None:
            routed = self._handle_confirmation_answer(text, input_mode, turn_id, pending_confirmation)
            if routed is not None:
                return routed

        pending_slot = self.context.session_state.get("pending_slot")
        if isinstance(pending_slot, dict):
            return self._handle_pending_slot(text, input_mode, turn_id, pending_slot)

        intent = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
        if intent.action not in _LEARNING_WRITE_ACTIONS and self.knowledge.has_learned_response(text):
            intent = replace(
                intent,
                action="LearnedResponseRecall",
                confidence=max(intent.confidence, 0.99),
                parameters={**intent.parameters, "source": "learned_response_store"},
            )
        return self._process_intent(text, input_mode, turn_id, intent)

    def _process_intent(self, text: str, input_mode: str, turn_id: str, intent: Intent) -> ConversationTurn:
        self.context.record_intent(intent.action)
        self.events.publish(
            Event(
                type=EventTypes.INTENT_RECOGNIZED,
                source="brain.intent_router",
                payload={
                    "turn_id": turn_id,
                    "action": intent.action,
                    "application": intent.application,
                    "resource": intent.resource,
                    "priority": intent.priority.value,
                    "confidence": intent.confidence,
                    "target_agent": intent.target_agent,
                },
            )
        )

        decision = self.decision_engine.decide(intent, self.context.snapshot())
        self.events.publish(
            Event(
                type=EventTypes.DECISION_MADE,
                source="brain.decision",
                payload={"turn_id": turn_id, "decision": decision.type.value, "reason": decision.reason},
            )
        )

        self.memory.record_turn(text, intent)

        if decision.type in {DecisionType.ASK_CLARIFICATION, DecisionType.WAIT, DecisionType.REJECT}:
            if decision.question:
                if intent.requires_confirmation:
                    confirmation_binding = self._confirmation_binding(intent)
                    confirmation = self.context.add_pending_confirmation(
                        decision.question,
                        {
                            "turn_id": turn_id,
                            "intent": intent,
                            "unclear_replies": 0,
                            "confirmation_binding": confirmation_binding,
                        },
                    )
                    self.events.publish(
                        Event(
                            type=EventTypes.CONFIRMATION_REQUESTED,
                            source="brain.conversation",
                            payload={
                                "turn_id": turn_id,
                                "confirmation_id": confirmation.id,
                                "question": confirmation.question,
                                "intent": intent.action,
                            },
                        )
                    )
                elif decision.reason == "Missing application slot.":
                    self.context.session_state["pending_slot"] = {
                        "slot": "application",
                        "intent": intent,
                        "turn_id": turn_id,
                    }
                    self.events.publish(
                        Event(
                            type=EventTypes.CONTEXT_UPDATED,
                            source="brain.conversation",
                            payload={"turn_id": turn_id, "pending_slot": "application", "intent": intent.action},
                        )
                    )
            return ConversationTurn(
                user_text=text,
                input_mode=input_mode,
                intent=intent,
                decision=decision,
                plan=None,
                message=decision.question or decision.reason,
            )

        if intent.action in CONVERSATIONAL_ACTIONS:
            answer = self.knowledge.answer(intent, self.dispatcher, self.context.snapshot(), self.memory)
            answered_intent = replace(
                intent,
                parameters={
                    **intent.parameters,
                    "response_category": answer.category,
                    "response_variables": answer.variables,
                },
            )
            return ConversationTurn(
                user_text=text,
                input_mode=input_mode,
                intent=answered_intent,
                decision=decision,
                plan=None,
                message=answer.message,
            )

        if decision.should_remember:
            self.memory.remember(text, tags=("user_request", intent.action))

        plan = self.planner.create_plan(intent)
        self._publish_plan(plan, turn_id)

        results: tuple[AgentResult, ...] = ()
        if self.auto_dispatch and decision.type in {DecisionType.EXECUTE_IMMEDIATELY, DecisionType.DELEGATE}:
            results = self._dispatch_plan(plan)

        return ConversationTurn(
            user_text=text,
            input_mode=input_mode,
            intent=intent,
            decision=decision,
            plan=plan,
            message="Plan created and delegated." if results else "Plan created.",
            dispatched_results=results,
        )

    def _handle_confirmation_answer(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        confirmation: PendingConfirmation,
    ) -> ConversationTurn | None:
        answer = _classify_confirmation_answer(text)
        if answer == "affirmative":
            return self._resolve_confirmed(text, input_mode, turn_id, confirmation)
        if answer == "negative":
            return self._resolve_cancelled(text, input_mode, turn_id, confirmation, "User cancelled the action.")
        return self._handle_unclear_confirmation_answer(text, input_mode, turn_id, confirmation)

    def _handle_pending_slot(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        pending_slot: dict[str, object],
    ) -> ConversationTurn:
        intent = pending_slot.get("intent")
        if not isinstance(intent, Intent):
            self.context.session_state.pop("pending_slot", None)
            fresh = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
            return self._process_intent(text, input_mode, turn_id, fresh)

        application = resolve_application_alias(text.strip())
        if not application:
            self.context.session_state.pop("pending_slot", None)
            fresh = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
            return self._process_intent(text, input_mode, turn_id, fresh)

        self.context.session_state.pop("pending_slot", None)
        filled_intent = replace(intent, application=application, raw_text=f"{intent.raw_text} {text}".strip())
        self.events.publish(
            Event(
                type=EventTypes.CONTEXT_UPDATED,
                source="brain.conversation",
                payload={"turn_id": turn_id, "filled_slot": "application", "application": application},
            )
        )
        return self._process_intent(text, input_mode, turn_id, filled_intent)

    def _resolve_confirmed(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        confirmation: PendingConfirmation,
    ) -> ConversationTurn:
        self.context.resolve_confirmation(confirmation.id)
        self.events.publish(
            Event(
                type=EventTypes.CONFIRMATION_RESOLVED,
                source="brain.conversation",
                payload={
                    "turn_id": turn_id,
                    "confirmation_id": confirmation.id,
                    "resolution": "confirmed",
                },
            )
        )
        intent = confirmation.metadata.get("intent")
        if not isinstance(intent, Intent):
            intent = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
        elif intent.requires_confirmation:
            binding = confirmation.metadata.get("confirmation_binding")
            bound_parameters = {}
            if isinstance(binding, dict):
                bound_parameters = {
                    "confirmation_action_hash": binding.get("action_hash"),
                    "confirmation_expires_at": binding.get("expires_at"),
                }
            intent = replace(
                intent,
                parameters={**intent.parameters, "confirmed": True, **bound_parameters},
                requires_confirmation=False,
            )
        return self._process_intent(text, input_mode, turn_id, intent)

    def _resolve_cancelled(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        confirmation: PendingConfirmation,
        reason: str,
    ) -> ConversationTurn:
        self.context.resolve_confirmation(confirmation.id)
        self.events.publish(
            Event(
                type=EventTypes.CONFIRMATION_RESOLVED,
                source="brain.conversation",
                payload={
                    "turn_id": turn_id,
                    "confirmation_id": confirmation.id,
                    "resolution": "cancelled",
                    "reason": reason,
                },
            )
        )
        self.events.publish(
            Event(
                type=EventTypes.TASK_CANCELLED,
                source="brain.conversation",
                payload={
                    "turn_id": turn_id,
                    "confirmation_id": confirmation.id,
                    "reason": reason,
                },
            )
        )
        intent = _confirmation_response_intent(text)
        decision = Decision(type=DecisionType.REJECT, reason=reason)
        self.memory.record_turn(text, intent)
        return ConversationTurn(
            user_text=text,
            input_mode=input_mode,
            intent=intent,
            decision=decision,
            plan=None,
            message=reason,
        )

    def _handle_unclear_confirmation_answer(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        confirmation: PendingConfirmation,
    ) -> ConversationTurn | None:
        unclear_replies = int(confirmation.metadata.get("unclear_replies", 0)) + 1
        if unclear_replies < self.max_unclear_confirmation_replies:
            self.context.update_confirmation_metadata(
                confirmation.id,
                {**confirmation.metadata, "unclear_replies": unclear_replies},
            )
            intent = _confirmation_response_intent(text)
            decision = Decision(
                type=DecisionType.WAIT,
                reason="Confirmation answer was unclear.",
                question=confirmation.question,
            )
            self.memory.record_turn(text, intent)
            return ConversationTurn(
                user_text=text,
                input_mode=input_mode,
                intent=intent,
                decision=decision,
                plan=None,
                message=confirmation.question,
            )

        self.context.resolve_confirmation(confirmation.id)
        self.events.publish(
            Event(
                type=EventTypes.CONFIRMATION_RESOLVED,
                source="brain.conversation",
                payload={
                    "turn_id": turn_id,
                    "confirmation_id": confirmation.id,
                    "resolution": "cancelled",
                    "reason": "Too many unclear confirmation replies.",
                },
            )
        )
        fresh_intent = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
        if fresh_intent.confidence >= 0.5:
            return self._process_intent(text, input_mode, turn_id, fresh_intent)

        decision = Decision(
            type=DecisionType.REJECT,
            reason="Confirmation was cancelled after too many unclear replies.",
        )
        self.memory.record_turn(text, fresh_intent)
        return ConversationTurn(
            user_text=text,
            input_mode=input_mode,
            intent=fresh_intent,
            decision=decision,
            plan=None,
            message=decision.reason,
        )

    def _expire_pending_confirmations(self, turn_id: str) -> None:
        now = datetime.now(timezone.utc)
        for confirmation in tuple(self.context.pending_confirmations.values()):
            if now - confirmation.created_at <= self.confirmation_ttl:
                continue
            self.context.resolve_confirmation(confirmation.id)
            self.events.publish(
                Event(
                    type=EventTypes.CONFIRMATION_EXPIRED,
                    source="brain.conversation",
                    payload={
                        "turn_id": turn_id,
                        "confirmation_id": confirmation.id,
                        "created_at": confirmation.created_at.isoformat(),
                    },
                )
            )

    def _publish_plan(self, plan: Plan, turn_id: str) -> None:
        self.events.publish(
            Event(
                type=EventTypes.PLAN_CREATED,
                source="brain.planner",
                payload={"turn_id": turn_id, "plan_id": plan.id, "task_count": len(plan.tasks)},
            )
        )
        for task in plan.tasks:
            self.events.publish(
                Event(
                    type=EventTypes.TASK_CREATED,
                    source="brain.planner",
                    payload={
                        "plan_id": plan.id,
                        "task_id": task.id,
                        "description": task.description,
                        "action": task.action,
                        "mode": task.mode.value,
                        "target_agent": task.target_agent,
                        "depends_on": task.depends_on,
                        "timeout_seconds": task.timeout_seconds,
                    },
                )
            )

    def _dispatch_plan(self, plan: Plan) -> tuple[AgentResult, ...]:
        completed: set[str] = set()
        failed: set[str] = set()
        results: list[AgentResult] = []

        for task in plan.tasks:
            if not self._dependencies_satisfied(task, completed):
                failed.add(task.id)
                results.append(AgentResult(False, "Task dependencies were not satisfied.", {"task_id": task.id}))
                continue

            self.context.mark_task_running(task.id, task.description, task.target_agent)
            result = self.dispatcher.dispatch(task, plan.id)
            self.context.mark_task_finished(task.id)
            results.append(result)
            if result.success:
                completed.add(task.id)
            else:
                failed.add(task.id)

            if task.mode == TaskMode.SEQUENTIAL and failed:
                break

        if failed:
            self.logger.error("plan_failed plan_id=%s failed_tasks=%s", plan.id, sorted(failed))
        return tuple(results)

    def _dependencies_satisfied(self, task: Task, completed: set[str]) -> bool:
        return all(dependency in completed for dependency in task.depends_on)

    def _confirmation_binding(self, intent: Intent) -> dict[str, object]:
        expires_at = datetime.now(timezone.utc) + self.confirmation_ttl
        if intent.action == "CloseApplication":
            agent = "desktop"
            capability = "desktop.application.close"
            action = "close_application"
            target = intent.application
            parameters = {"application": intent.application}
        else:
            agent = intent.target_agent
            action = _action_to_command(intent.action)
            capability = str(intent.parameters.get("capability") or action)
            target = intent.application or intent.resource
            parameters = {
                "text": intent.raw_text,
                "application": intent.application,
                "resource": intent.resource,
            }
        return {
            "agent": agent,
            "capability": capability,
            "action": action,
            "target": target,
            "expires_at": expires_at.isoformat(),
            "action_hash": action_tuple_hash(
                agent=agent,
                capability=capability,
                action=action,
                target=target,
                parameters=parameters,
                session=None,
                expires_at=expires_at,
            ),
        }


ConfirmationAnswer = Literal["affirmative", "negative", "unclear"]


_LEARNING_WRITE_ACTIONS = frozenset(
    {
        "TeachResponse",
        "LearnTopic",
        "TryHackMeLessonCapture",
        "TryHackMeLearningPlan",
        "TryHackMeProgressReview",
        "Remember",
    }
)


def _classify_confirmation_answer(text: str) -> ConfirmationAnswer:
    normalized = " ".join(text.lower().strip().split())
    affirmative_answers = {
        "yes",
        "y",
        "confirm",
        "confirmed",
        "do it",
        "continue",
        "proceed",
        "ok",
        "okay",
        "sure",
        "go ahead",
        "כן",
        "מאשר",
        "אשר",
        "תמשיך",
        "בצע",
    }
    negative_answers = {
        "no",
        "n",
        "cancel",
        "stop",
        "do not",
        "don't",
        "never mind",
        "abort",
        "לא",
        "בטל",
        "עצור",
        "אל",
    }
    if normalized in affirmative_answers:
        return "affirmative"
    if normalized in negative_answers:
        return "negative"
    return "unclear"


def _confirmation_response_intent(text: str) -> Intent:
    return Intent(
        action="ConfirmationResponse",
        raw_text=text,
        confidence=1.0,
    )
