from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest

from agents.base import AgentCommand, AgentResult, BaseAgent
from brain.context import ContextEngine
from brain.conversation import ConversationEngine
from brain.decision import DecisionEngine, DecisionType
from brain.dispatcher import AgentDispatcher
from brain.intent_router import DEFAULT_PATTERNS, IntentPattern, IntentRouter
from brain.memory_manager import MemoryManager
from brain.planner import Planner
from core.events import EventBus, EventTypes
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory
from permissions import AgentManifest, Capability, PermissionTier


class EchoAgent(BaseAgent):
    name = "echo"
    permission_manifest = AgentManifest(
        agent="echo",
        capabilities=(
            Capability("echo", PermissionTier.T1),
            Capability("dangerous_echo", PermissionTier.T2, requires_confirmation=True),
        ),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "echo ok", {"action": command.action})


def make_engine() -> tuple[ConversationEngine, EventBus, ContextEngine]:
    events = EventBus()
    context = ContextEngine()
    dispatcher = AgentDispatcher(events)
    dispatcher.register_agent(EchoAgent())
    engine = ConversationEngine(
        intent_router=IntentRouter(
            patterns=(
                IntentPattern("DangerousEcho", ("danger",), domain="echo", requires_confirmation=True),
                IntentPattern("Echo", ("echo",), domain="echo"),
                *DEFAULT_PATTERNS,
            )
        ),
        decision_engine=DecisionEngine(),
        planner=Planner(),
        memory=MemoryManager(ShortTermMemory(), LongTermMemory(), events),
        context=context,
        dispatcher=dispatcher,
        events=events,
        confirmation_ttl_seconds=300,
        max_unclear_confirmation_replies=2,
    )
    return engine, events, context


class ConversationConfirmationTests(unittest.TestCase):
    def test_confirmation_yes_dispatches_original_intent(self) -> None:
        engine, events, context = make_engine()

        first = engine.handle_text("danger operation")
        second = engine.handle_text("yes")

        self.assertEqual(first.decision.type, DecisionType.ASK_CLARIFICATION)
        self.assertFalse(context.pending_confirmations)
        self.assertEqual(second.intent.action, "DangerousEcho")
        self.assertIsNotNone(second.plan)
        self.assertEqual(len(second.dispatched_results), 1)
        self.assertTrue(second.dispatched_results[0].success)
        self.assertIn(EventTypes.CONFIRMATION_RESOLVED, [event.type for event in events.history()])
        self.assertIn(EventTypes.TASK_DISPATCHED, [event.type for event in events.history()])

    def test_confirmation_no_cancels_and_next_request_is_processed(self) -> None:
        engine, events, context = make_engine()

        engine.handle_text("danger operation")
        cancelled = engine.handle_text("no")
        next_turn = engine.handle_text("Open Spotify")

        self.assertFalse(context.pending_confirmations)
        self.assertEqual(cancelled.decision.type, DecisionType.REJECT)
        self.assertIsNone(cancelled.plan)
        self.assertEqual(next_turn.intent.action, "OpenApplication")
        self.assertIsNotNone(next_turn.plan)
        self.assertIn(EventTypes.TASK_CANCELLED, [event.type for event in events.history()])

    def test_unclear_replies_reask_then_auto_cancel_without_deadlock(self) -> None:
        engine, events, context = make_engine()

        engine.handle_text("danger operation")
        reasked = engine.handle_text("maybe")
        auto_cancelled = engine.handle_text("not sure")
        next_turn = engine.handle_text("Open Spotify")

        self.assertEqual(reasked.decision.type, DecisionType.WAIT)
        self.assertEqual(auto_cancelled.decision.type, DecisionType.REJECT)
        self.assertFalse(context.pending_confirmations)
        self.assertEqual(next_turn.intent.action, "OpenApplication")
        self.assertIsNotNone(next_turn.plan)
        self.assertIn(EventTypes.CONFIRMATION_RESOLVED, [event.type for event in events.history()])

    def test_expired_confirmation_is_cancelled_and_new_request_processed(self) -> None:
        engine, events, context = make_engine()

        engine.handle_text("danger operation")
        confirmation = context.oldest_pending_confirmation()
        self.assertIsNotNone(confirmation)
        expired = replace(
            confirmation,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        )
        context.pending_confirmations[confirmation.id] = expired

        turn = engine.handle_text("Open Spotify")

        self.assertFalse(context.pending_confirmations)
        self.assertEqual(turn.intent.action, "OpenApplication")
        self.assertIsNotNone(turn.plan)
        self.assertIn(EventTypes.CONFIRMATION_EXPIRED, [event.type for event in events.history()])

    def test_two_clear_requests_in_sequence_both_dispatch(self) -> None:
        engine, events, context = make_engine()

        first = engine.handle_text("echo first")
        second = engine.handle_text("echo second")

        self.assertFalse(context.pending_confirmations)
        self.assertIsNotNone(first.plan)
        self.assertIsNotNone(second.plan)
        dispatched_events = [event for event in events.history() if event.type == EventTypes.TASK_DISPATCHED]
        self.assertGreaterEqual(len(dispatched_events), 2)

    def test_missing_application_slot_is_filled_without_false_confirmation(self) -> None:
        engine, events, context = make_engine()

        first = engine.handle_text("תפתחי אפליקציה")
        second = engine.handle_text("Spotify")

        self.assertEqual(first.decision.type, DecisionType.ASK_CLARIFICATION)
        self.assertFalse(context.pending_confirmations)
        self.assertNotIn("pending_slot", context.session_state)
        self.assertEqual(second.intent.action, "OpenApplication")
        self.assertEqual(second.intent.application, "Spotify")
        self.assertIsNotNone(second.plan)
        self.assertNotIn("ConfirmationResponse", [event.payload.get("action") for event in events.history()])

    def test_close_application_requires_confirmation_then_dispatches_original_intent(self) -> None:
        engine, events, context = make_engine()

        first = engine.handle_text("close Finder")
        second = engine.handle_text("yes")

        self.assertEqual(first.decision.type, DecisionType.ASK_CLARIFICATION)
        self.assertFalse(context.pending_confirmations)
        self.assertEqual(second.intent.action, "CloseApplication")
        self.assertIsNotNone(second.plan)
        self.assertEqual(second.plan.tasks[0].action, "close_application")
        self.assertEqual(second.plan.tasks[0].capability, "desktop.application.close")
        self.assertIn(EventTypes.CONFIRMATION_RESOLVED, [event.type for event in events.history()])


if __name__ == "__main__":
    unittest.main()
