import unittest

from brain.context import ContextEngine
from brain.decision import DecisionEngine, DecisionType
from brain.intent_router import IntentRouter


class DecisionEngineTests(unittest.TestCase):
    def test_decides_to_delegate_complete_intent(self) -> None:
        intent = IntentRouter().classify("Open Spotify and play my Night playlist")
        decision = DecisionEngine().decide(intent, ContextEngine().snapshot())

        self.assertEqual(decision.type, DecisionType.DELEGATE)

    def test_asks_clarification_for_unclear_intent(self) -> None:
        intent = IntentRouter().classify("blue umbrella")
        decision = DecisionEngine().decide(intent, ContextEngine().snapshot())

        self.assertEqual(decision.type, DecisionType.ASK_CLARIFICATION)
        self.assertIsNotNone(decision.question)


if __name__ == "__main__":
    unittest.main()

