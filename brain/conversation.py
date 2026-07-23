"""Conversation orchestration for NELA OS."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from agents.base import AgentResult
from brain.context import ContextEngine
from brain.decision import Decision, DecisionEngine, DecisionType
from brain.dispatcher import AgentDispatcher
from brain.intent_router import Intent, IntentRouter
from brain.memory_manager import MemoryManager
from brain.planner import Plan, Planner, Task, TaskMode
from core.events import Event, EventBus, EventTypes


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
    ) -> None:
        self.intent_router = intent_router
        self.decision_engine = decision_engine
        self.planner = planner
        self.memory = memory
        self.context = context
        self.dispatcher = dispatcher
        self.events = events
        self.auto_dispatch = auto_dispatch
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

        intent = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
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
                self.context.add_pending_confirmation(decision.question, {"turn_id": turn_id})
            return ConversationTurn(
                user_text=text,
                input_mode=input_mode,
                intent=intent,
                decision=decision,
                plan=None,
                message=decision.question or decision.reason,
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
