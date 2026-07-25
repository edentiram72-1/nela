import unittest

from brain.intent_router import IntentRouter, Priority


class IntentRecognitionTests(unittest.TestCase):
    def test_recognizes_structured_music_intent(self) -> None:
        intent = IntentRouter().classify("Open Spotify and play my Night playlist now")

        self.assertEqual(intent.action, "PlayMedia")
        self.assertEqual(intent.application, "Spotify")
        self.assertEqual(intent.resource, "Night")
        self.assertEqual(intent.priority, Priority.HIGH)
        self.assertEqual(intent.target_agent, "spotify")

    def test_low_confidence_unknown_request_requires_more_context_later(self) -> None:
        intent = IntentRouter().classify("blue umbrella")

        self.assertEqual(intent.action, "GeneralRequest")
        self.assertLess(intent.confidence, 0.5)

    def test_does_not_match_keywords_inside_other_words(self) -> None:
        intent = IntentRouter().classify("Open display settings")

        self.assertEqual(intent.action, "OpenApplication")
        self.assertEqual(intent.application, "Display Settings")

    def test_recognizes_close_application_intent(self) -> None:
        intent = IntentRouter().classify("NELA, close Finder")

        self.assertEqual(intent.action, "CloseApplication")
        self.assertEqual(intent.application, "Finder")
        self.assertTrue(intent.requires_confirmation)

    def test_recognizes_switch_application_intent(self) -> None:
        intent = IntentRouter().classify("switch to Spotify")

        self.assertEqual(intent.action, "SwitchApplication")
        self.assertEqual(intent.application, "Spotify")

    def test_recognizes_hebrew_open_application_intent(self) -> None:
        intent = IntentRouter().classify("נלה, תפתחי את Spotify")

        self.assertEqual(intent.action, "OpenApplication")
        self.assertEqual(intent.application, "Spotify")
        self.assertEqual(intent.target_agent, "spotify")

    def test_resolves_hebrew_application_alias(self) -> None:
        intent = IntentRouter().classify("נלה, תפתחי את ספוטיפיי")

        self.assertEqual(intent.action, "OpenApplication")
        self.assertEqual(intent.application, "Spotify")

    def test_hebrew_identity_question_is_conversational(self) -> None:
        intent = IntentRouter().classify("מי את?")

        self.assertEqual(intent.action, "IdentityQuestion")
        self.assertGreaterEqual(intent.confidence, 0.5)

    def test_hebrew_capabilities_question_is_conversational(self) -> None:
        intent = IntentRouter().classify("מה את יודעת לעשות?")

        self.assertEqual(intent.action, "CapabilitiesQuestion")

    def test_hebrew_agent_status_question_is_conversational(self) -> None:
        intent = IntentRouter().classify("איזה סוכנים מחוברים?")

        self.assertEqual(intent.action, "AgentStatusQuestion")

    def test_unknown_question_gets_general_question_intent(self) -> None:
        intent = IntentRouter().classify("מה קורה בירח?")

        self.assertEqual(intent.action, "GeneralQuestion")
        self.assertGreaterEqual(intent.confidence, 0.5)


if __name__ == "__main__":
    unittest.main()
